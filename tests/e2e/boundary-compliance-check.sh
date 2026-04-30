#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

scan_paths=()
for path in skills commands agents; do
    if [[ -e "$path" ]]; then
        scan_paths+=("$path")
    fi
done

if [[ ${#scan_paths[@]} -eq 0 ]]; then
    echo "No agent-facing prompt assets found."
    exit 1
fi

if command -v rg >/dev/null 2>&1; then
    search_cmd=(rg -n -i
        -e 'completion grants?'
        -e 'completion granted'
        -e 'grant(ed|s)? completion authority'
        -e 'has completion authority'
        -e 'authoritative gate decision'
        -e 'authoritative impact statement'
        -e 'final governance decision'
        -e 'final gate decision'
    )
    filter_cmd=(rg -v -i
        -e 'never'
        -e 'do not'
        -e 'does not'
        -e 'must not'
        -e 'cannot'
        -e 'can not'
        -e 'not final authority'
        -e 'not authoritative'
        -e 'only, NOT'
        -e 'draft inputs'
        -e '不得'
        -e '不可以'
        -e '不能'
        -e '禁止'
    )
else
    search_cmd=(grep -R -n -I -i -E
        'completion grants?|completion granted|grant(ed|s)? completion authority|has completion authority|authoritative gate decision|authoritative impact statement|final governance decision|final gate decision'
    )
    filter_cmd=(grep -E -i -v
        'never|do not|does not|must not|cannot|can not|not final authority|not authoritative|only, NOT|draft inputs|不得|不可以|不能|禁止'
    )
fi

candidate_matches="$("${search_cmd[@]}" "${scan_paths[@]}" || true)"

if [[ -z "$candidate_matches" ]]; then
    echo "No candidate authority-drift phrases found."
    exit 0
fi

violations="$(printf '%s\n' "$candidate_matches" | "${filter_cmd[@]}" || true)"

if [[ -n "$violations" ]]; then
    echo "Boundary compliance violations detected:"
    printf '%s\n' "$violations"
    exit 1
fi

echo "Boundary compliance check passed."
exit 0
