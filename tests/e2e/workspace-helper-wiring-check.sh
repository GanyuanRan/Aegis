#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

fail() {
    echo "Workspace helper wiring check failed: $1"
    exit 1
}

require_pattern() {
    local file="$1"
    local pattern="$2"
    if ! grep -qF "$pattern" "$file"; then
        fail "$file missing pattern: $pattern"
    fi
}

require_pattern "skills/using-aegis/SKILL.md" "aegis-workspace.py init"
require_pattern "skills/using-aegis/SKILL.md" "aegis-workspace.py new-work"
require_pattern "skills/using-aegis/SKILL.md" "aegis-workspace.py check"

require_pattern "skills/brainstorming/SKILL.md" "aegis-workspace.py append-index"
require_pattern "skills/brainstorming/SKILL.md" "aegis-workspace.py check"

require_pattern "skills/writing-plans/SKILL.md" "aegis-workspace.py append-index"
require_pattern "skills/writing-plans/SKILL.md" "aegis-workspace.py check"

require_pattern "skills/test-driven-development/SKILL.md" "aegis-workspace.py new-work"

require_pattern "skills/systematic-debugging/SKILL.md" "aegis-workspace.py new-work"
require_pattern "skills/systematic-debugging/SKILL.md" "aegis-workspace.py add-evidence"
require_pattern "skills/systematic-debugging/SKILL.md" "aegis-workspace.py check"

require_pattern "skills/long-task-continuation/SKILL.md" "aegis-workspace.py new-work"
require_pattern "skills/long-task-continuation/SKILL.md" "aegis-workspace.py add-checkpoint"
require_pattern "skills/long-task-continuation/SKILL.md" "aegis-workspace.py add-evidence"
require_pattern "skills/long-task-continuation/SKILL.md" "aegis-workspace.py add-drift-check"
require_pattern "skills/long-task-continuation/SKILL.md" "aegis-workspace.py bundle"

require_pattern "skills/verification-before-completion/SKILL.md" "aegis-workspace.py bundle"
require_pattern "skills/verification-before-completion/SKILL.md" "aegis-workspace.py check"

echo "Workspace helper skill wiring check passed."
