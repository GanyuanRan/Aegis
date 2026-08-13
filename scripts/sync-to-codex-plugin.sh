#!/usr/bin/env bash
#
# sync-to-codex-plugin.sh
#
# Sync this aegis checkout → prime-radiant-inc/openai-codex-plugins.
# Clones the fork fresh into a temp dir, rsyncs tracked source plugin content
# (including committed Codex files under .codex-plugin/ and assets/), commits,
# pushes a sync branch, and opens a PR.
# Path/user agnostic — auto-detects the source checkout from script location.
#
# Deterministic: running twice against the same source SHA produces PRs with
# identical diffs, so two back-to-back runs can verify the tool itself.
#
# Usage:
#   ./scripts/sync-to-codex-plugin.sh                              # full run
#   ./scripts/sync-to-codex-plugin.sh -n                           # dry run
#   ./scripts/sync-to-codex-plugin.sh -y                           # skip confirm
#   ./scripts/sync-to-codex-plugin.sh --local PATH                 # existing checkout
#   ./scripts/sync-to-codex-plugin.sh --base BRANCH                # default: main
#   ./scripts/sync-to-codex-plugin.sh --bootstrap                  # create plugin dir if missing
#
# Bootstrap mode: skips the "plugin must exist on base" requirement and creates
# plugins/aegis/ when absent, then copies the tracked plugin files from this
# checkout just like a normal sync.
#
# Requires: bash, git, gh (authenticated), python3.

set -euo pipefail

# =============================================================================
# Config — edit as source or canonical plugin shape evolves
# =============================================================================

FORK="prime-radiant-inc/openai-codex-plugins"
DEFAULT_BASE="main"
DEST_REL="plugins/aegis"

# Paths in source that should NOT land in the embedded plugin.
# All patterns use a leading "/" to anchor them to the source root.
# Unanchored patterns like "scripts/" would match any directory named
# "scripts" at any depth. Anchoring keeps top-level exclusions precise.
# (.DS_Store is intentionally unanchored — Finder creates them everywhere.)
EXCLUDES=(
  # Dotfiles and infra — top-level only
  "/.claude/"
  "/.claude-plugin/"
  "/.codebuddy-plugin/"
  "/.codex/"
  "/.cursor/"
  "/.cursor-plugin/"
  "/.git/"
  "/.gitattributes"
  "/.github/"
  "/.gitignore"
  "/.opencode/"
  "/.version-bump.json"
  "/.windsurf/"
  "/.worktrees/"
  ".DS_Store"

  # Root ceremony files
  "/AGENTS.md"
  "/CHANGELOG.md"
  "/CLAUDE.md"
  "/RELEASE-NOTES.md"
  "/package.json"

  # Directories not shipped by canonical Codex plugins
  "/commands/"
  "/docs/"
  "/hooks/"
  "/lib/"
  "/scripts/"
  "/tests/"
  "/tmp/"
)

# =============================================================================
# Sync manifest helpers
# =============================================================================

is_excluded_path() {
  local path="$1"
  local pattern
  local normalized

  for pattern in "${EXCLUDES[@]}"; do
    if [[ "$pattern" == /* ]]; then
      normalized="${pattern#/}"
      if [[ "$normalized" == */ ]]; then
        [[ "$path" == "$normalized"* ]] && return 0
      else
        [[ "$path" == "$normalized" ]] && return 0
      fi
      continue
    fi

    [[ "$path" == "$pattern" || "$path" == */"$pattern" ]] && return 0
  done

  return 1
}

write_sync_manifest() {
  local manifest_path="$1"
  local path

  : > "$manifest_path"

  while IFS= read -r -d '' path; do
    is_excluded_path "$path" && continue
    printf '%s\n' "$path" >> "$manifest_path"
  done < <(git -C "$UPSTREAM" ls-files --cached --others --exclude-standard -z)

  LC_ALL=C sort -o "$manifest_path" "$manifest_path"
}

run_sync_engine() {
  local mode="$1"
  local source_root="$2"
  local dest_root="$3"
  local manifest_path="$4"

  "${PYTHON_CMD[@]}" - "$mode" "$source_root" "$dest_root" "$manifest_path" <<'PY'
import filecmp
import os
import shutil
import sys

mode, source_root, dest_root, manifest_path = sys.argv[1:5]

with open(manifest_path, encoding="utf-8") as handle:
    source_rel_paths = [line.rstrip("\n") for line in handle if line.rstrip("\n")]

source_rel_set = set(source_rel_paths)
dest_rel_paths = []

if os.path.isdir(dest_root):
    for walk_root, _dirs, files in os.walk(dest_root):
        rel_root = os.path.relpath(walk_root, dest_root)
        for name in files:
            rel_path = name if rel_root == "." else os.path.join(rel_root, name)
            dest_rel_paths.append(rel_path.replace("\\", "/"))

dest_rel_set = set(dest_rel_paths)

planned_lines = []

for rel_path in sorted(dest_rel_set - source_rel_set):
    planned_lines.append(f"*deleting {rel_path}")

for rel_path in source_rel_paths:
    source_path = os.path.join(source_root, rel_path)
    dest_path = os.path.join(dest_root, rel_path)

    if not os.path.exists(dest_path):
        planned_lines.append(f">f+++++++++ {rel_path}")
        continue

    if not filecmp.cmp(source_path, dest_path, shallow=False):
        planned_lines.append(f">f..change.. {rel_path}")

for line in planned_lines:
    print(line)

if mode != "apply":
    raise SystemExit(0)

for rel_path in sorted(dest_rel_set - source_rel_set, key=lambda item: (item.count("/"), item), reverse=True):
    dest_path = os.path.join(dest_root, rel_path)
    if os.path.lexists(dest_path):
        os.remove(dest_path)

if os.path.isdir(dest_root):
    for walk_root, dirs, files in os.walk(dest_root, topdown=False):
        if walk_root == dest_root:
            continue
        if not dirs and not files:
            os.rmdir(walk_root)

for rel_path in source_rel_paths:
    source_path = os.path.join(source_root, rel_path)
    dest_path = os.path.join(dest_root, rel_path)
    dest_parent = os.path.dirname(dest_path)
    if dest_parent:
        os.makedirs(dest_parent, exist_ok=True)
    if not os.path.exists(dest_path) or not filecmp.cmp(source_path, dest_path, shallow=False):
        shutil.copy2(source_path, dest_path)
PY
}

# =============================================================================
# Args
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
UPSTREAM="$(cd "$SCRIPT_DIR/.." && pwd)"
BASE="$DEFAULT_BASE"
DRY_RUN=0
YES=0
LOCAL_CHECKOUT=""
BOOTSTRAP=0

usage() {
  sed -n '/^# Usage:/,/^# Requires:/s/^# \{0,1\}//p' "$0"
  exit "${1:-0}"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -n|--dry-run)  DRY_RUN=1; shift ;;
    -y|--yes)      YES=1; shift ;;
    --local)       LOCAL_CHECKOUT="$2"; shift 2 ;;
    --base)        BASE="$2"; shift 2 ;;
    --bootstrap)   BOOTSTRAP=1; shift ;;
    -h|--help)     usage 0 ;;
    *)             echo "Unknown arg: $1" >&2; usage 2 ;;
  esac
done

# =============================================================================
# Preflight
# =============================================================================

die() { echo "ERROR: $*" >&2; exit 1; }

command -v git >/dev/null     || die "git not found in PATH"
command -v gh >/dev/null      || die "gh not found — install GitHub CLI"

if command -v python3 >/dev/null 2>&1 && python3 -V >/dev/null 2>&1; then
  PYTHON_CMD=(python3)
elif command -v py >/dev/null 2>&1 && py -3 -V >/dev/null 2>&1; then
  PYTHON_CMD=(py -3)
elif command -v python >/dev/null 2>&1 && python -V >/dev/null 2>&1; then
  PYTHON_CMD=(python)
else
  die "no runnable python interpreter found in PATH"
fi

gh auth status >/dev/null 2>&1 || die "gh not authenticated — run 'gh auth login'"

[[ -d "$UPSTREAM/.git" ]]         || die "upstream '$UPSTREAM' is not a git checkout"
[[ -f "$UPSTREAM/.codex-plugin/plugin.json" ]] || die "committed Codex manifest missing at $UPSTREAM/.codex-plugin/plugin.json"

# Read the upstream version from the committed Codex manifest.
UPSTREAM_VERSION="$("${PYTHON_CMD[@]}" -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$UPSTREAM/.codex-plugin/plugin.json")"
[[ -n "$UPSTREAM_VERSION" ]] || die "could not read 'version' from committed Codex manifest"

UPSTREAM_BRANCH="$(cd "$UPSTREAM" && git branch --show-current)"
UPSTREAM_SHA="$(cd "$UPSTREAM" && git rev-parse HEAD)"
UPSTREAM_SHORT="$(cd "$UPSTREAM" && git rev-parse --short HEAD)"

confirm() {
  [[ $YES -eq 1 ]] && return 0
  read -rp "$1 [y/N] " ans
  [[ "$ans" == "y" || "$ans" == "Y" ]]
}

if [[ "$UPSTREAM_BRANCH" != "main" ]]; then
  echo "WARNING: upstream is on '$UPSTREAM_BRANCH', not 'main'"
  confirm "Sync from '$UPSTREAM_BRANCH' anyway?" || exit 1
fi

UPSTREAM_STATUS="$(cd "$UPSTREAM" && git status --porcelain)"
if [[ -n "$UPSTREAM_STATUS" ]]; then
  echo "WARNING: upstream has uncommitted changes:"
  echo "$UPSTREAM_STATUS" | sed 's/^/  /'
  echo "Sync will use working-tree state, not HEAD ($UPSTREAM_SHORT)."
  confirm "Continue anyway?" || exit 1
fi

# =============================================================================
# Prepare destination (clone fork fresh, or use --local)
# =============================================================================

CLEANUP_DIR=""
SYNC_MANIFEST=""
cleanup() {
  if [[ -n "$CLEANUP_DIR" ]]; then
    rm -rf "$CLEANUP_DIR"
  fi
}
trap cleanup EXIT

if [[ -n "$LOCAL_CHECKOUT" ]]; then
  DEST_REPO="$(cd "$LOCAL_CHECKOUT" && pwd)"
  [[ -d "$DEST_REPO/.git" ]] || die "--local path '$DEST_REPO' is not a git checkout"
else
  echo "Cloning $FORK..."
  CLEANUP_DIR="$(mktemp -d)"
  DEST_REPO="$CLEANUP_DIR/openai-codex-plugins"
  gh repo clone "$FORK" "$DEST_REPO" >/dev/null
fi

DEST="$DEST_REPO/$DEST_REL"
PREVIEW_REPO="$DEST_REPO"
PREVIEW_DEST="$DEST"

overlay_destination_paths() {
  local repo="$1"
  local path
  local source_path
  local preview_path

  while IFS= read -r -d '' path; do
    source_path="$repo/$path"
    preview_path="$PREVIEW_REPO/$path"

    if [[ -e "$source_path" ]]; then
      mkdir -p "$(dirname "$preview_path")"
      cp -R "$source_path" "$preview_path"
    else
      rm -rf "$preview_path"
    fi
  done
}

copy_local_destination_overlay() {
  overlay_destination_paths "$DEST_REPO" < <(
    git -C "$DEST_REPO" diff --name-only -z -- "$DEST_REL"
  )
  overlay_destination_paths "$DEST_REPO" < <(
    git -C "$DEST_REPO" diff --cached --name-only -z -- "$DEST_REL"
  )
  overlay_destination_paths "$DEST_REPO" < <(
    git -C "$DEST_REPO" ls-files --others --exclude-standard -z -- "$DEST_REL"
  )
  overlay_destination_paths "$DEST_REPO" < <(
    git -C "$DEST_REPO" ls-files --others --ignored --exclude-standard -z -- "$DEST_REL"
  )
}

local_checkout_has_uncommitted_destination_changes() {
  [[ -n "$(git -C "$DEST_REPO" status --porcelain=1 --untracked-files=all --ignored=matching -- "$DEST_REL")" ]]
}

prepare_preview_checkout() {
  if [[ -n "$LOCAL_CHECKOUT" ]]; then
    [[ -n "$CLEANUP_DIR" ]] || CLEANUP_DIR="$(mktemp -d)"
    PREVIEW_REPO="$CLEANUP_DIR/preview"
    git -c core.autocrlf=false clone -q --no-local "$DEST_REPO" "$PREVIEW_REPO"
    PREVIEW_DEST="$PREVIEW_REPO/$DEST_REL"
  fi

  git -C "$PREVIEW_REPO" checkout -q "$BASE" 2>/dev/null || die "base branch '$BASE' doesn't exist in $FORK"
  if [[ -n "$LOCAL_CHECKOUT" ]]; then
    copy_local_destination_overlay
  fi
  if [[ $BOOTSTRAP -ne 1 ]]; then
    [[ -d "$PREVIEW_DEST" ]] || die "base branch '$BASE' has no '$DEST_REL/' — use --bootstrap, or pass --base <branch>"
  fi
}

prepare_apply_checkout() {
  git -C "$DEST_REPO" checkout -q "$BASE" 2>/dev/null || die "base branch '$BASE' doesn't exist in $FORK"
  if [[ $BOOTSTRAP -ne 1 ]]; then
    [[ -d "$DEST" ]] || die "base branch '$BASE' has no '$DEST_REL/' — use --bootstrap, or pass --base <branch>"
  fi
}

apply_to_preview_checkout() {
  if [[ $BOOTSTRAP -eq 1 ]]; then
    mkdir -p "$PREVIEW_DEST"
  fi

  run_sync_engine apply "$UPSTREAM" "$PREVIEW_DEST" "$SYNC_MANIFEST"
}

preview_checkout_has_changes() {
  local preview_output

  preview_output="$(run_sync_engine preview "$UPSTREAM" "$PREVIEW_DEST" "$SYNC_MANIFEST")"
  [[ -n "$preview_output" ]]
}

prepare_preview_checkout

TIMESTAMP="$(date -u +%Y%m%d-%H%M%S)"
if [[ $BOOTSTRAP -eq 1 ]]; then
  SYNC_BRANCH="bootstrap/aegis-${UPSTREAM_SHORT}-${TIMESTAMP}"
else
  SYNC_BRANCH="sync/aegis-${UPSTREAM_SHORT}-${TIMESTAMP}"
fi

# =============================================================================
# Build sync manifest
# =============================================================================

[[ -n "$CLEANUP_DIR" ]] || CLEANUP_DIR="$(mktemp -d)"
SYNC_MANIFEST="$CLEANUP_DIR/sync-manifest.txt"
write_sync_manifest "$SYNC_MANIFEST"

# =============================================================================
# Dry run preview (always shown)
# =============================================================================

echo ""
echo "Upstream: $UPSTREAM ($UPSTREAM_BRANCH @ $UPSTREAM_SHORT)"
echo "Version:  $UPSTREAM_VERSION"
echo "Fork:     $FORK"
echo "Base:     $BASE"
echo "Branch:   $SYNC_BRANCH"
if [[ $BOOTSTRAP -eq 1 ]]; then
  echo "Mode:     BOOTSTRAP (creating plugins/aegis/ when absent)"
fi
echo ""
echo "=== Preview (rsync --dry-run) ==="
run_sync_engine preview "$UPSTREAM" "$PREVIEW_DEST" "$SYNC_MANIFEST"
echo "=== End preview ==="
echo ""

if [[ $DRY_RUN -eq 1 ]]; then
  echo ""
  echo "Dry run only. Nothing was changed or pushed."
  exit 0
fi

# =============================================================================
# Apply
# =============================================================================

echo ""
confirm "Apply changes, push branch, and open PR?" || { echo "Aborted."; exit 1; }

echo ""
if [[ -n "$LOCAL_CHECKOUT" ]]; then
  if local_checkout_has_uncommitted_destination_changes; then
    die "local checkout has uncommitted changes under '$DEST_REL' — commit, stash, or discard them before syncing"
  fi

  if ! preview_checkout_has_changes; then
    echo "No changes — embedded plugin was already in sync with upstream $UPSTREAM_SHORT (v$UPSTREAM_VERSION)."
    exit 0
  fi
fi

prepare_apply_checkout
cd "$DEST_REPO"
git checkout -q -b "$SYNC_BRANCH"
echo "Syncing upstream content..."
if [[ $BOOTSTRAP -eq 1 ]]; then
  mkdir -p "$DEST"
fi
run_sync_engine apply "$UPSTREAM" "$DEST" "$SYNC_MANIFEST"

# Bail early if nothing actually changed
cd "$DEST_REPO"
if [[ -z "$(git status --porcelain "$DEST_REL")" ]]; then
  echo "No changes — embedded plugin was already in sync with upstream $UPSTREAM_SHORT (v$UPSTREAM_VERSION)."
  exit 0
fi

# =============================================================================
# Commit, push, open PR
# =============================================================================

git add "$DEST_REL"

if [[ $BOOTSTRAP -eq 1 ]]; then
  COMMIT_TITLE="bootstrap aegis v$UPSTREAM_VERSION from source main @ $UPSTREAM_SHORT"
  PR_BODY="Initial bootstrap of the aegis plugin from source \`main\` @ \`$UPSTREAM_SHORT\` (v$UPSTREAM_VERSION).

Creates \`plugins/aegis/\` by copying the tracked plugin files from source, including \`.codex-plugin/plugin.json\` and \`assets/\`.

Run via: \`scripts/sync-to-codex-plugin.sh --bootstrap\`
Source commit: https://github.com/GanyuanRan/Aegis/commit/$UPSTREAM_SHA

This is a one-time bootstrap. Subsequent syncs will be normal (non-bootstrap) runs using the same tracked source plugin files."
else
  COMMIT_TITLE="sync aegis v$UPSTREAM_VERSION from source main @ $UPSTREAM_SHORT"
  PR_BODY="Automated sync from aegis source \`main\` @ \`$UPSTREAM_SHORT\` (v$UPSTREAM_VERSION).

Copies the tracked plugin files from source, including the committed Codex manifest and assets.

Run via: \`scripts/sync-to-codex-plugin.sh\`
Source commit: https://github.com/GanyuanRan/Aegis/commit/$UPSTREAM_SHA

Running the sync tool again against the same source SHA should produce a PR with an identical diff — use that to verify the tool is behaving."
fi

git commit --quiet -m "$COMMIT_TITLE

Automated sync via scripts/sync-to-codex-plugin.sh
Source:   https://github.com/GanyuanRan/Aegis/commit/$UPSTREAM_SHA
Branch:   $SYNC_BRANCH"

echo "Pushing $SYNC_BRANCH to $FORK..."
git push -u origin "$SYNC_BRANCH" --quiet

echo "Opening PR..."
PR_URL="$(gh pr create \
  --repo "$FORK" \
  --base "$BASE" \
  --head "$SYNC_BRANCH" \
  --title "$COMMIT_TITLE" \
  --body "$PR_BODY")"

PR_NUM="${PR_URL##*/}"
DIFF_URL="https://github.com/$FORK/pull/$PR_NUM/files"

echo ""
echo "PR opened: $PR_URL"
echo "Diff view: $DIFF_URL"
