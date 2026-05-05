#!/usr/bin/env bash
set -euo pipefail

LOG="${1:-}"
PATTERN="${2:-}"
WINDOW="${3:-40}"

usage() {
    echo "Usage: $0 <log-file> <pattern> [window-lines]" >&2
}

if [[ -z "$LOG" || -z "$PATTERN" ]]; then
    usage
    exit 2
fi

if [[ -d "$LOG" ]]; then
    echo "Refusing directory input: $LOG" >&2
    exit 2
fi

if [[ ! -f "$LOG" ]]; then
    echo "Log file not found: $LOG" >&2
    exit 2
fi

if ! [[ "$WINDOW" =~ ^[0-9]+$ ]]; then
    echo "Window must be a non-negative integer: $WINDOW" >&2
    exit 2
fi

if (( WINDOW > 200 )); then
    echo "Refusing window larger than 200 lines: $WINDOW" >&2
    exit 2
fi

if command -v rg >/dev/null 2>&1; then
    matches="$(rg -n "$PATTERN" "$LOG" || true)"
else
    matches="$(grep -nE "$PATTERN" "$LOG" || true)"
fi

match_line="$(printf '%s\n' "$matches" | tail -n 1 | cut -d: -f1)"

if [[ -z "$match_line" ]]; then
    echo "No match for pattern: $PATTERN" >&2
    exit 1
fi

start=$(( match_line > WINDOW ? match_line - WINDOW : 1 ))
end=$(( match_line + WINDOW ))

echo "match_line=$match_line window=$start,$end log=$LOG"
nl -ba "$LOG" | sed -n "${start},${end}p"
