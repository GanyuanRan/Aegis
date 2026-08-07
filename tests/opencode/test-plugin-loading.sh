#!/usr/bin/env bash
# Test: Plugin Loading
# Verifies that the aegis plugin loads correctly in OpenCode
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Test: Plugin Loading ==="

# Source setup to create isolated environment
source "$SCRIPT_DIR/setup.sh"

# Trap to cleanup on exit
trap cleanup_test_env EXIT

plugin_link="$OPENCODE_CONFIG_DIR/plugins/aegis.js"

# Test 1: Verify plugin file exists and is registered
echo "Test 1: Checking plugin registration..."
if [ -L "$plugin_link" ]; then
    echo "  [PASS] Plugin symlink exists"
elif [ -f "$plugin_link" ]; then
    echo "  [PASS] Plugin file exists"
else
    echo "  [FAIL] Plugin registration not found at $plugin_link"
    exit 1
fi

# Verify registered plugin payload exists
if [ -f "$plugin_link" ]; then
    echo "  [PASS] Registered plugin payload exists"
else
    echo "  [FAIL] Registered plugin payload does not exist"
    exit 1
fi

# Test 2: Verify skills directory is populated
echo "Test 2: Checking skills directory..."
skill_count=$(find "$AEGIS_SKILLS_DIR" -name "SKILL.md" | wc -l)
if [ "$skill_count" -gt 0 ]; then
    echo "  [PASS] Found $skill_count skills"
else
    echo "  [FAIL] No skills found in $AEGIS_SKILLS_DIR"
    exit 1
fi

# Test 3: Check using-aegis skill exists (critical for bootstrap)
echo "Test 3: Checking using-aegis skill (required for bootstrap)..."
if [ -f "$AEGIS_SKILLS_DIR/using-aegis/SKILL.md" ]; then
    echo "  [PASS] using-aegis skill exists"
else
    echo "  [FAIL] using-aegis skill not found (required for bootstrap)"
    exit 1
fi

# Test 4: Verify plugin JavaScript syntax (basic check)
echo "Test 4: Checking plugin JavaScript syntax..."
if node --check "$AEGIS_PLUGIN_FILE" 2>/dev/null; then
    echo "  [PASS] Plugin JavaScript syntax is valid"
else
    echo "  [FAIL] Plugin has JavaScript syntax errors"
    exit 1
fi

# Test 5: Verify bootstrap text does not reference a hardcoded skills path
echo "Test 5: Checking bootstrap does not advertise a wrong skills path..."
if grep -q 'configDir}/skills/aegis/' "$AEGIS_PLUGIN_FILE"; then
    echo "  [FAIL] Plugin still references old configDir skills path"
    exit 1
else
    echo "  [PASS] Plugin does not advertise a misleading skills path"
fi

# Test 6: Verify personal test skill was created
echo "Test 6: Checking test fixtures..."
if [ -f "$OPENCODE_PERSONAL_SKILLS_DIR/personal-test/SKILL.md" ]; then
    echo "  [PASS] Personal test skill fixture created"
else
    echo "  [FAIL] Personal test skill fixture not found"
    exit 1
fi

# Test 7: Verify configured canonical method-pack root is preferred
echo "Test 7: Checking canonical method-pack root preference..."
canonical_root="$TEST_HOME/canonical-aegis"
mkdir -p "$canonical_root"
cp -r "$REPO_ROOT/skills" "$canonical_root/"
mkdir -p "$TEST_HOME/.config/aegis"
cat > "$TEST_HOME/.config/aegis/config.toml" <<EOF
activation_mode = "auto"
tdd_mode = "auto"
method_pack_root = "$canonical_root"
workspace_helper = "$canonical_root/scripts/aegis-workspace.py"
EOF

mkdir -p "$canonical_root/skills/using-aegis"
printf '\nCANONICAL_ROOT_MARKER_24680\n' >> "$canonical_root/skills/using-aegis/SKILL.md"

mirror_dir="$OPENCODE_CONFIG_DIR/skills"
rm -rf "$mirror_dir"

node --input-type=module <<'EOF'
import path from 'path';
import { pathToFileURL } from 'url';

const pluginPath = process.env.AEGIS_PLUGIN_FILE;
const module = await import(pathToFileURL(pluginPath).href);
await module.AegisPlugin({ client: {}, directory: path.dirname(pluginPath) });
EOF

if grep -q 'CANONICAL_ROOT_MARKER_24680' "$mirror_dir/using-aegis/SKILL.md"; then
    echo "  [PASS] Plugin mirrors from configured canonical method-pack root"
else
    echo "  [FAIL] Plugin did not prefer configured canonical method-pack root"
    exit 1
fi

# Test 8: Verify bootstrap contains the routing contract
echo "Test 8: Checking bootstrap routing contract..."
if grep -q 'ROUTING CONTRACT' "$AEGIS_PLUGIN_FILE" \
    && grep -q 'Route: fast-path' "$AEGIS_PLUGIN_FILE"; then
    echo "  [PASS] Bootstrap declares a routing contract with fast-path escape"
else
    echo "  [FAIL] Bootstrap routing contract markers missing"
    exit 1
fi

# Test 9: Verify routing guard hooks are present
echo "Test 9: Checking routing guard hooks..."
if grep -q 'tool.execute.after' "$AEGIS_PLUGIN_FILE" \
    && grep -q 'AEGIS_ROUTING_GUARD' "$AEGIS_PLUGIN_FILE" \
    && grep -q 'sawSkillCall' "$AEGIS_PLUGIN_FILE"; then
    echo "  [PASS] Routing guard hooks and marker are present"
else
    echo "  [FAIL] Routing guard implementation missing"
    exit 1
fi

# Test 10: Verify routing guard behavior (functional)
echo "Test 10: Checking routing guard behavior..."
aegis_config_file="$TEST_HOME/.config/aegis/config.toml"
saved_config=""
if [ -f "$aegis_config_file" ]; then
    saved_config=$(cat "$aegis_config_file")
fi
cat > "$aegis_config_file" <<EOF
activation_mode = "auto"
EOF

node --input-type=module <<'EOF'
import path from 'path';
import { pathToFileURL } from 'url';

const pluginPath = process.env.AEGIS_PLUGIN_FILE;
const module = await import(pathToFileURL(pluginPath).href);
const hooks = await module.AegisPlugin({ client: {}, directory: path.dirname(pluginPath) });
const after = hooks['tool.execute.after'];
const before = hooks['tool.execute.before'];

const check = (name, condition) => {
    if (!condition) {
        console.error(`  [FAIL] ${name}`);
        process.exit(1);
    }
    console.log(`  [PASS] ${name}`);
};

// s1: first non-readonly call without skill load must be flagged
let out = { title: '', output: 'ok' };
await after({ tool: 'bash', sessionID: 's1', callID: 'c1', args: {} }, out);
check('guard flags first non-readonly call', out.output.includes('AEGIS_ROUTING_GUARD'));

// s1: second non-readonly call must not be flagged again
out = { title: '', output: 'ok2' };
await after({ tool: 'edit', sessionID: 's1', callID: 'c2', args: {} }, out);
check('guard fires once per session', !out.output.includes('AEGIS_ROUTING_GUARD'));

// s2: skill load before work suppresses the guard
out = { title: '', output: 'ok' };
await before({ tool: 'skill', sessionID: 's2', callID: 'c0' }, {});
await after({ tool: 'bash', sessionID: 's2', callID: 'c1', args: {} }, out);
check('skill load suppresses guard', !out.output.includes('AEGIS_ROUTING_GUARD'));

// s3: readonly tools never trigger the guard
out = { title: '', output: 'ok' };
await after({ tool: 'read', sessionID: 's3', callID: 'c1', args: {} }, out);
check('readonly tools are exempt', !out.output.includes('AEGIS_ROUTING_GUARD'));
out = { title: '', output: 'ok' };
await after({ tool: 'bash', sessionID: 's3', callID: 'c2', args: {} }, out);
check('guard still flags later work', out.output.includes('AEGIS_ROUTING_GUARD'));
EOF
if [ $? -ne 0 ]; then
    exit 1
fi

# Test 10b: explicit mode disables the guard
cat > "$aegis_config_file" <<EOF
activation_mode = "explicit"
EOF

node --input-type=module <<'EOF'
import path from 'path';
import { pathToFileURL } from 'url';

const pluginPath = process.env.AEGIS_PLUGIN_FILE;
const module = await import(pathToFileURL(pluginPath).href);
const hooks = await module.AegisPlugin({ client: {}, directory: path.dirname(pluginPath) });
const after = hooks['tool.execute.after'];

const out = { title: '', output: 'ok' };
await after({ tool: 'bash', sessionID: 's4', callID: 'c1', args: {} }, out);
if (out.output.includes('AEGIS_ROUTING_GUARD')) {
    console.error('  [FAIL] explicit mode must disable the routing guard');
    process.exit(1);
}
console.log('  [PASS] explicit mode disables the routing guard');
EOF
if [ $? -ne 0 ]; then
    exit 1
fi

# Restore the previous config for later tests
if [ -n "$saved_config" ]; then
    printf '%s\n' "$saved_config" > "$aegis_config_file"
else
    rm -f "$aegis_config_file"
fi

echo ""
echo "=== All plugin loading tests passed ==="
