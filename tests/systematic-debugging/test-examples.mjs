// Requires Node.js 22.13+ for native TypeScript stripping; no npm dependencies.
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { readFile, mkdtemp, mkdir, symlink, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { stripTypeScriptTypes } from 'node:module';

const loadTS = (source) => import(`data:text/javascript,${encodeURIComponent(stripTypeScriptTypes(source))}`);
const exampleRoot = new URL('../../skills/systematic-debugging/', import.meta.url);
const waits = await loadTS(await readFile(new URL('condition-based-waiting-example.ts', exampleRoot), 'utf8'));

for (const [name, invoke] of [
  ['event', (manager, ms) => waits.waitForEvent(manager, 'thread', 'READY', ms)],
  ['count', (manager, ms) => waits.waitForEventCount(manager, 'thread', 'READY', 1, ms)],
  ['match', (manager, ms) => waits.waitForEventMatch(manager, 'thread', e => e.type === 'READY', 'ready', ms)],
]) {
  test(`${name}: delayed match resolves`, async () => {
    let reads = 0;
    const event = { type: 'READY' };
    const result = await invoke({ getEvents: () => ++reads > 1 ? [event] : [] }, 1000);
    assert.deepEqual(result, name === 'count' ? [event] : event);
  });
  test(`${name}: later getter failure rejects`, async () => {
    let reads = 0;
    const error = new Error('storage unavailable');
    await assert.rejects(invoke({ getEvents() { if (++reads > 1) throw error; return []; } }, 100), error);
  });
  test(`${name}: absent match times out`, async () => {
    await assert.rejects(invoke({ getEvents: () => [] }, 10), /Timeout waiting/);
  });
}

test('later predicate failure rejects', async () => {
  let reads = 0;
  const error = new Error('bad event');
  await assert.rejects(waits.waitForEventMatch(
    { getEvents: () => ++reads > 1 ? [{ type: 'READY' }] : [] }, 'thread',
    () => { throw error; }, 'ready', 100,
  ), error);
});

test('environment guard distinguishes descendants from sibling prefixes', async () => {
  const text = await readFile(new URL('defense-in-depth.md', exampleRoot), 'utf8');
  const source = text.split('### Layer 3:')[1].match(/```typescript\n([\s\S]*?)```/)[1];
  const root = await mkdtemp(join(tmpdir(), 'aegis-path-'));
  const temp = join(root, 'temp');
  const nested = join(temp, 'nested');
  const sibling = join(root, 'temp-evil');
  const escape = join(temp, 'escape');
  await mkdir(nested, { recursive: true });
  await mkdir(sibling);
  await symlink(sibling, escape, process.platform === 'win32' ? 'junction' : 'dir');
  const originalEnv = process.env.NODE_ENV;
  try {
    // Supply imports for the standalone documentation excerpt and a fixture temp root.
    const module = await loadTS(`import { normalize, resolve, relative, isAbsolute, sep } from 'node:path';
      import { realpath } from 'node:fs/promises';
      const tmpdir = () => ${JSON.stringify(temp)};
      ${source}\nexport { gitInit };`);
    process.env.NODE_ENV = 'test';
    await module.gitInit(nested);
    await assert.rejects(module.gitInit(sibling), /Refusing git init/);
    await assert.rejects(module.gitInit(temp), /Refusing git init/);
    await assert.rejects(module.gitInit(escape), /Refusing git init/);
  } finally {
    if (originalEnv === undefined) delete process.env.NODE_ENV;
    else process.env.NODE_ENV = originalEnv;
    await rm(root, { recursive: true, force: true });
  }
});
