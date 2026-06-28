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


SEMANTIC_ALIASES = {
    "change necessity": ["change necessity", "变更必要性"],
    "user-visible need": [
        "user-visible need",
        "用户可见需要",
        "用户可见的需要",
        "用户可见需求",
        "用户可见问题",
    ],
    "no-change / non-code option": [
        "no-change / non-code option",
        "no-change option",
        "non-code option",
        "非代码方式",
        "非代码选项",
        "非代码方案",
        "不改代码",
        "配置或文档不能修复",
        "文档不能修复",
        "配置不能修复",
    ],
    "why code change is necessary": [
        "why code change is necessary",
        "code change is necessary",
        "why code change",
        "为什么需要代码变更",
        "代码变更是必要",
        "代码变更必要",
        "代码改动是必要",
        "必要代码改动",
        "不覆盖已有已存/异步输入",
        "不能覆盖已有已存/异步输入",
        "不能修复已进入代码路径",
        "不能修复运行时归一化",
        "不能修复运行时展示",
        "不能修复运行时显示",
        "不能修复运行行为",
        "不能修复 ui",
        "无法修复渲染路径",
        "无法改变这个输入在渲染路径里的输出",
        "不改代码只能接受错误展示",
        "不能阻止已有",
        "不能稳定拦住",
        "拦住已有输入值",
        "不能防止页面再次收到",
        "非代码选项只能要求上游",
        "上游永不传该值",
        "负责默认化",
        "负责把未设置值归一化",
        "问题不在页面渲染层",
        "归一化函数已经是这个行为的 owner",
        "只能解释现象，不能修复",
        "不能防止再次出现",
        "补丁的必要性",
        "必要性和边界",
        "现有展示入口已经有归一化 owner",
    ],
    "minimum change boundary": [
        "minimum change boundary",
        "minimum boundary",
        "最小变更边界",
        "最小代码边界",
        "最小边界",
        "最小补丁",
        "边界是",
    ],
    "decision: code-change": [
        "decision: code-change",
        "decision：code-change",
        "decision: code change",
        "decision code-change",
        "code-change",
        "代码变更",
        "源码变更",
        "改源码",
        "改实现",
        "应用这个小补丁",
        "尝试应用这个小补丁",
        "尝试应用补丁",
        "我会做两个小改动",
        "现在改这两处",
        "最小补丁是",
        "补一条回归测试",
        "补测试",
    ],
    "canonical owner": [
        "canonical owner",
        "canonicalowner",
        "canonical owner:",
        "normalizetheme",
        "src/settings.js",
        "改一个 owner",
    ],
    "evidence": [
        "evidence",
        "证据",
        "证据链",
        "复现",
        "复现命令输出",
        "复现命令返回",
        "复现结果",
    ],
    "before source edits": [
        "before source edits",
        "before source edit",
        "before code changes",
        "before editing",
        "源码编辑前",
        "写源代码前",
    ],
    "source edit intention": [
        "source edit intention",
        "now edit only",
        "i now only edit",
        "i will now edit",
        "我现在只改",
        "现在我只改",
        "我现在会做",
        "现在我会做",
        "我现在会改",
        "现在改这两处",
        "我准备只改这两处",
        "我会做两行级别的小改动",
        "现在做这个小改动",
        "现在做两处小改",
    ],
    "fix boundary": [
        "fix boundary",
        "source edit intention",
        "修复边界",
        "修复边界很窄",
        "边界是",
        "最小必要代码变更是在",
        "now edit only",
        "i now only edit",
        "i will now edit",
        "我现在只改",
        "现在我只改",
        "我现在会做",
        "现在我会做",
        "我现在会改",
        "现在改这两处",
        "我准备只改这两处",
        "我会做两行级别的小改动",
        "现在做这个小改动",
        "现在做两处小改",
    ],
}


def aliases_for(term):
    return SEMANTIC_ALIASES.get(term.lower(), [term])


def find_term_index(text_lower, term, start=0):
    indexes = [
        index
        for alias in aliases_for(term)
        for index in [text_lower.find(alias.lower(), start)]
        if index != -1
    ]
    return min(indexes) if indexes else -1


def contains_term(text_lower, term):
    return find_term_index(text_lower, term) != -1


def check_ordered_terms(groups, text_lower):
    present = []
    missing = []
    for group in groups:
        cursor = 0
        group_present = []
        failed = False
        for term in group:
            index = find_term_index(text_lower, term, cursor)
            if index == -1:
                failed = True
                break
            group_present.append(term)
            cursor = index + 1
        if failed:
            missing.append(group)
        else:
            present.append(group)
    return present, missing


transcript_path = Path(sys.argv[1])
expected_behavior = load_json(sys.argv[2])
expected_artifacts = load_json(sys.argv[3]) if sys.argv[3] else {}
summary_json_path = Path(sys.argv[4]) if sys.argv[4] else None
quiet = sys.argv[5] == "1"

entries = load_jsonl(str(transcript_path))
combined_text, combined_lower, assistant_lower, detected_skills = normalize_texts(entries)

expected_sequence = expected_behavior.get("skillSequence", [])
required_skills = expected_behavior.get("requiredSkills", [])
must_contain = expected_behavior.get("mustContain", [])
assistant_must_contain = expected_behavior.get("assistantMustContain", [])
assistant_ordered_terms = expected_behavior.get("assistantOrderedTerms", [])
must_not_contain = expected_behavior.get("mustNotContain", [])
required_artifacts = expected_artifacts.get("requiredArtifacts", [])

skill_sequence_pass, matched_sequence = check_skill_sequence(expected_sequence, detected_skills)

required_skills_present = [skill for skill in required_skills if skill in detected_skills]
required_skills_missing = [skill for skill in required_skills if skill not in detected_skills]
present_terms = [term for term in must_contain if contains_term(combined_lower, term)]
missing_terms = [term for term in must_contain if not contains_term(combined_lower, term)]
assistant_present_terms = [
    term for term in assistant_must_contain if contains_term(assistant_lower, term)
]
assistant_missing_terms = [
    term for term in assistant_must_contain if not contains_term(assistant_lower, term)
]
assistant_ordered_present, assistant_ordered_missing = check_ordered_terms(
    assistant_ordered_terms,
    assistant_lower,
)
forbidden_terms = [term for term in must_not_contain if term.lower() in combined_lower]

artifact_hits = [artifact for artifact in required_artifacts if artifact.lower() in combined_lower]
artifact_misses = [artifact for artifact in required_artifacts if artifact.lower() not in combined_lower]

summary = {
    "transcript": str(transcript_path),
    "detectedSkills": detected_skills,
    "expectedSkillSequence": expected_sequence,
    "matchedSkillSequence": matched_sequence,
    "skillSequencePass": skill_sequence_pass,
    "requiredSkillsPresent": required_skills_present,
    "requiredSkillsMissing": required_skills_missing,
    "requiredSkillsPass": not required_skills_missing,
    "mustContainPresent": present_terms,
    "mustContainMissing": missing_terms,
    "mustContainPass": not missing_terms,
    "assistantMustContainPresent": assistant_present_terms,
    "assistantMustContainMissing": assistant_missing_terms,
    "assistantMustContainPass": not assistant_missing_terms,
    "assistantOrderedTermsPresent": assistant_ordered_present,
    "assistantOrderedTermsMissing": assistant_ordered_missing,
    "assistantOrderedTermsPass": not assistant_ordered_missing,
    "mustNotContainHits": forbidden_terms,
    "mustNotContainPass": not forbidden_terms,
    "requiredArtifactsPresent": artifact_hits,
    "requiredArtifactsMissing": artifact_misses,
    "artifactPass": not artifact_misses,
}
summary["overallPass"] = (
    summary["skillSequencePass"]
    and summary["requiredSkillsPass"]
    and summary["mustContainPass"]
    and summary["assistantMustContainPass"]
    and summary["assistantOrderedTermsPass"]
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
    print(f"Required skills present: {', '.join(required_skills_present) if required_skills_present else '(none)'}")
    print(f"Required skills missing: {', '.join(required_skills_missing) if required_skills_missing else '(none)'}")
    print(f"Must contain present: {', '.join(present_terms) if present_terms else '(none)'}")
    print(f"Must contain missing: {', '.join(missing_terms) if missing_terms else '(none)'}")
    print(f"Assistant must contain present: {', '.join(assistant_present_terms) if assistant_present_terms else '(none)'}")
    print(f"Assistant must contain missing: {', '.join(assistant_missing_terms) if assistant_missing_terms else '(none)'}")
    print(f"Assistant ordered terms present: {assistant_ordered_present if assistant_ordered_present else '(none)'}")
    print(f"Assistant ordered terms missing: {assistant_ordered_missing if assistant_ordered_missing else '(none)'}")
    print(f"Must not contain hits: {', '.join(forbidden_terms) if forbidden_terms else '(none)'}")
    print(f"Artifacts present: {', '.join(artifact_hits) if artifact_hits else '(none)'}")
    print(f"Artifacts missing: {', '.join(artifact_misses) if artifact_misses else '(none)'}")
    print(f"OVERALL: {'PASS' if summary['overallPass'] else 'FAIL'}")

sys.exit(0 if summary["overallPass"] else 1)
PY
