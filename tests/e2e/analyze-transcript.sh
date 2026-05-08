#!/usr/bin/env bash
set -euo pipefail

python_cmd() {
    if command -v python3 >/dev/null 2>&1 && python3 -V >/dev/null 2>&1; then
        python3 "$@"
        return
    fi

    if command -v py >/dev/null 2>&1 && py -3 -V >/dev/null 2>&1; then
        py -3 "$@"
        return
    fi

    python "$@"
}

TRANSCRIPT_PATH=""
EXPECTED_BEHAVIOR_PATH=""
EXPECTED_ARTIFACTS_PATH=""
SUMMARY_JSON_PATH=""
QUIET=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --transcript)
            TRANSCRIPT_PATH="$2"
            shift 2
            ;;
        --expected-behavior)
            EXPECTED_BEHAVIOR_PATH="$2"
            shift 2
            ;;
        --expected-artifacts)
            EXPECTED_ARTIFACTS_PATH="$2"
            shift 2
            ;;
        --summary-json)
            SUMMARY_JSON_PATH="$2"
            shift 2
            ;;
        --quiet)
            QUIET=1
            shift
            ;;
        --help|-h)
            echo "Usage: $0 --transcript <file> --expected-behavior <file> [--expected-artifacts <file>] [--summary-json <file>] [--quiet]"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [[ -z "$TRANSCRIPT_PATH" || -z "$EXPECTED_BEHAVIOR_PATH" ]]; then
    echo "ERROR: --transcript and --expected-behavior are required"
    exit 1
fi

python_cmd - "$TRANSCRIPT_PATH" "$EXPECTED_BEHAVIOR_PATH" "$EXPECTED_ARTIFACTS_PATH" "$SUMMARY_JSON_PATH" "$QUIET" <<'PY'
import json
import sys
from pathlib import Path


def flatten_strings(value):
    if isinstance(value, str):
        yield value
        return
    if isinstance(value, dict):
        for item in value.values():
            yield from flatten_strings(item)
        return
    if isinstance(value, list):
        for item in value:
            yield from flatten_strings(item)


def load_json(path_str):
    if not path_str:
        return {}
    return json.loads(Path(path_str).read_text(encoding="utf-8"))


def load_jsonl(path_str):
    entries = []
    with Path(path_str).open(encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            entries.append(json.loads(line))
    return entries


def normalize_texts(entries):
    text_chunks = []
    assistant_chunks = []
    detected_skills = []

    for entry in entries:
        tool_result = entry.get("toolUseResult")
        if isinstance(tool_result, dict):
            skill_name = tool_result.get("skill")
            if isinstance(skill_name, str) and skill_name not in detected_skills:
                detected_skills.append(skill_name)

        for chunk in flatten_strings(entry):
            text_chunks.append(chunk)

        if entry.get("type") == "assistant":
            for chunk in flatten_strings(entry):
                assistant_chunks.append(chunk)

    combined = "\n".join(text_chunks)
    combined_lower = combined.lower()
    assistant_combined = "\n".join(assistant_chunks)
    assistant_lower = assistant_combined.lower()
    return combined, combined_lower, assistant_lower, detected_skills


def check_skill_sequence(expected_sequence, detected_skills):
    matched = []
    cursor = 0

    for expected in expected_sequence:
        try:
            found_index = detected_skills.index(expected, cursor)
        except ValueError:
            return False, matched
        matched.append(expected)
        cursor = found_index + 1

    return True, matched


transcript_path = Path(sys.argv[1])
expected_behavior = load_json(sys.argv[2])
expected_artifacts = load_json(sys.argv[3]) if sys.argv[3] else {}
summary_json_path = Path(sys.argv[4]) if sys.argv[4] else None
quiet = sys.argv[5] == "1"

entries = load_jsonl(str(transcript_path))
combined_text, combined_lower, assistant_lower, detected_skills = normalize_texts(entries)

expected_sequence = expected_behavior.get("skillSequence", [])
must_contain = expected_behavior.get("mustContain", [])
assistant_must_contain = expected_behavior.get("assistantMustContain", [])
must_not_contain = expected_behavior.get("mustNotContain", [])
required_artifacts = expected_artifacts.get("requiredArtifacts", [])

skill_sequence_pass, matched_sequence = check_skill_sequence(expected_sequence, detected_skills)

present_terms = [term for term in must_contain if term.lower() in combined_lower]
missing_terms = [term for term in must_contain if term.lower() not in combined_lower]
assistant_present_terms = [
    term for term in assistant_must_contain if term.lower() in assistant_lower
]
assistant_missing_terms = [
    term for term in assistant_must_contain if term.lower() not in assistant_lower
]
forbidden_terms = [term for term in must_not_contain if term.lower() in combined_lower]

artifact_hits = [artifact for artifact in required_artifacts if artifact.lower() in combined_lower]
artifact_misses = [artifact for artifact in required_artifacts if artifact.lower() not in combined_lower]

summary = {
    "transcript": str(transcript_path),
    "detectedSkills": detected_skills,
    "expectedSkillSequence": expected_sequence,
    "matchedSkillSequence": matched_sequence,
    "skillSequencePass": skill_sequence_pass,
    "mustContainPresent": present_terms,
    "mustContainMissing": missing_terms,
    "mustContainPass": not missing_terms,
    "assistantMustContainPresent": assistant_present_terms,
    "assistantMustContainMissing": assistant_missing_terms,
    "assistantMustContainPass": not assistant_missing_terms,
    "mustNotContainHits": forbidden_terms,
    "mustNotContainPass": not forbidden_terms,
    "requiredArtifactsPresent": artifact_hits,
    "requiredArtifactsMissing": artifact_misses,
    "artifactPass": not artifact_misses,
}
summary["overallPass"] = (
    summary["skillSequencePass"]
    and summary["mustContainPass"]
    and summary["assistantMustContainPass"]
    and summary["mustNotContainPass"]
    and summary["artifactPass"]
)

if summary_json_path:
    summary_json_path.parent.mkdir(parents=True, exist_ok=True)
    summary_json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

if not quiet:
    print(f"Transcript: {transcript_path}")
    print(f"Detected skills: {', '.join(detected_skills) if detected_skills else '(none)'}")
    print(f"Expected sequence: {', '.join(expected_sequence) if expected_sequence else '(none)'}")
    print(f"Matched sequence: {', '.join(matched_sequence) if matched_sequence else '(none)'}")
    print(f"Must contain present: {', '.join(present_terms) if present_terms else '(none)'}")
    print(f"Must contain missing: {', '.join(missing_terms) if missing_terms else '(none)'}")
    print(f"Assistant must contain present: {', '.join(assistant_present_terms) if assistant_present_terms else '(none)'}")
    print(f"Assistant must contain missing: {', '.join(assistant_missing_terms) if assistant_missing_terms else '(none)'}")
    print(f"Must not contain hits: {', '.join(forbidden_terms) if forbidden_terms else '(none)'}")
    print(f"Artifacts present: {', '.join(artifact_hits) if artifact_hits else '(none)'}")
    print(f"Artifacts missing: {', '.join(artifact_misses) if artifact_misses else '(none)'}")
    print(f"OVERALL: {'PASS' if summary['overallPass'] else 'FAIL'}")

sys.exit(0 if summary["overallPass"] else 1)
PY
