#!/usr/bin/env bash
# Test: Shared Pi/OMP extension core
# Verifies the host-neutral bootstrap/guard logic in extensions/shared/
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SHARED_CORE="$REPO_ROOT/extensions/shared/aegis-bootstrap.ts"

echo "=== Test: Shared Pi/OMP Extension Core ==="

if [ ! -f "$SHARED_CORE" ]; then
    echo "  [FAIL] shared core missing at $SHARED_CORE"
    exit 1
fi

node --experimental-strip-types --input-type=module <<'EOF'
import path from 'node:path';
import fs from 'node:fs';
import os from 'node:os';
import { pathToFileURL } from 'node:url';

const corePath = path.resolve(process.env.SHARED_CORE);
const core = await import(pathToFileURL(corePath).href);

const check = (name, condition) => {
    if (!condition) {
        console.error(`  [FAIL] ${name}`);
        process.exit(1);
    }
    console.log(`  [PASS] ${name}`);
};

// Config defaults without any config file.
const testHome = fs.mkdtempSync(path.join(os.tmpdir(), 'aegis-core-test-'));
process.env.HOME = testHome;
delete process.env.AEGIS_ACTIVATION_MODE;
delete process.env.AEGIS_TDD_MODE;
let config = core.readConfig(testHome);
check('default config is auto/off', config.activationMode === 'auto' && config.tddMode === 'off');

// Config file values.
fs.mkdirSync(path.join(testHome, '.config', 'aegis'), { recursive: true });
fs.writeFileSync(path.join(testHome, '.config', 'aegis', 'config.toml'), 'activation_mode = "explicit"\ntdd_mode = "auto"\n');
config = core.readConfig(testHome);
check('config file values are honored', config.activationMode === 'explicit' && config.tddMode === 'auto');

// Env overrides config file.
process.env.AEGIS_ACTIVATION_MODE = 'auto';
config = core.readConfig(testHome);
check('env overrides config file', config.activationMode === 'auto' && config.tddMode === 'auto');

// Bootstrap assembly.
const body = core.stripFrontmatter(fs.readFileSync(process.env.USING_AEGIS_SKILL, 'utf8'));
check('frontmatter stripped', !body.includes('alwaysApply') && body.includes('Route: fast-path'));
const bootstrap = core.buildBootstrap(body, { tddMode: 'off', host: 'pi', toolMapping: 'TOOL_MAP' });
check('bootstrap contains marker', bootstrap.includes('EXTREMELY_IMPORTANT'));
check('bootstrap contains routing contract', bootstrap.includes('ROUTING CONTRACT'));
check('bootstrap contains fast-path escape', bootstrap.includes('Route: fast-path'));
check('bootstrap contains tool mapping', bootstrap.includes('TOOL_MAP'));
check('bootstrap contains tdd mode', bootstrap.includes('Aegis TDD mode: off'));

// Guard: skill load suppresses the marker.
const readonlyTools = ['read', 'grep', 'glob'];
let state = core.createGuardState();
let d = core.updateGuard(state, 'read', { path: '/x/skills/using-aegis/SKILL.md' }, readonlyTools);
check('reading a SKILL.md counts as skill load', d.state.sawSkillLoad === true && d.mark === false);
d = core.updateGuard(state, 'bash', { command: 'echo hi' }, readonlyTools);
check('skill load suppresses guard on later tool', d.mark === false && d.state.guardFired === false);

// Guard: skill:// URL counts as a skill load (OMP).
state = core.createGuardState();
d = core.updateGuard(state, 'read', { path: 'skill://using-aegis' }, readonlyTools);
check('skill:// URL counts as skill load', d.state.sawSkillLoad === true && d.mark === false);

// Guard: readonly tools never fire.
state = core.createGuardState();
d = core.updateGuard(state, 'grep', { pattern: 'x' }, readonlyTools);
check('readonly tool does not fire guard', d.mark === false);
d = core.updateGuard(state, 'bash', { command: 'echo hi' }, readonlyTools);
check('first non-readonly fires guard once', d.mark === true);
d = core.updateGuard(state, 'edit', { filePath: '/x' }, readonlyTools);
check('guard fires once per session', d.mark === false);

// Guard: explicit skill tool.
state = core.createGuardState();
d = core.updateGuard(state, 'skill', { name: 'brainstorming' }, readonlyTools);
check('skill tool counts as skill load', d.state.sawSkillLoad === true && d.mark === false);

// Adapter: context injection + guard wiring on a fake host API.
const fakePi = (() => {
    const handlers = {};
    return {
        handlers,
        on: (event, handler) => { handlers[event] = handler; },
    };
})();
core.createAegisHostAdapter(fakePi, { host: 'pi', readonlyTools });
const ctxHandler = fakePi.handlers['context'];
const toolCallHandler = fakePi.handlers['tool_call'];
const toolResultHandler = fakePi.handlers['tool_result'];

let result = await ctxHandler({ messages: [{ role: 'user', content: [{ type: 'text', text: 'hello' }] }] });
check('adapter injects bootstrap into first user message', result.messages[0].content[0].text.includes('EXTREMELY_IMPORTANT'));
result = await ctxHandler({ messages: [{ role: 'user', content: [{ type: 'text', text: 'already injected EXTREMELY_IMPORTANT' }] }] });
check('adapter deduplicates bootstrap', result === undefined);

await toolCallHandler({ toolName: 'bash', input: { command: 'ls' }, toolCallId: 't1' }, { sessionManager: { getSessionId: () => 's1' } });
result = await toolResultHandler({ toolCallId: 't1', content: [{ type: 'text', text: 'out' }] });
check('adapter guard appends marker on first non-readonly', result.content[0].text.includes('AEGIS_ROUTING_GUARD'));

await toolCallHandler({ toolName: 'edit', input: { filePath: '/x' }, toolCallId: 't2' }, { sessionManager: { getSessionId: () => 's1' } });
result = await toolResultHandler({ toolCallId: 't2', content: [{ type: 'text', text: 'out2' }] });
check('adapter guard fires once', result === undefined);

await toolCallHandler({ toolName: 'read', input: { path: 'skill://brainstorming' }, toolCallId: 't3' }, { sessionManager: { getSessionId: () => 's2' } });
await toolCallHandler({ toolName: 'bash', input: { command: 'ls' }, toolCallId: 't4' }, { sessionManager: { getSessionId: () => 's2' } });
result = await toolResultHandler({ toolCallId: 't4', content: [{ type: 'text', text: 'out' }] });
check('adapter skill load suppresses guard', result === undefined);

fs.rmSync(testHome, { recursive: true, force: true });
EOF
if [ $? -ne 0 ]; then
    exit 1
fi

echo ""
echo "=== Shared Pi/OMP extension core tests passed ==="
