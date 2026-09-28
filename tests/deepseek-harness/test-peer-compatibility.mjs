// Run against an installed DSH app-boot module; use the host's real range policy.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

if (!process.argv[2]) {
  throw new Error('Usage: node test-peer-compatibility.mjs <dsh-app-boot/lib/index.js>');
}
const { evaluatePluginCompatibility, getDshRuntimeVersion } = await import(
  pathToFileURL(resolve(process.argv[2])).href
);
const manifest = JSON.parse(readFileSync(new URL('../../package.json', import.meta.url), 'utf8'));
const peers = [
  '@deepseek-ai/dsh-agent',
  '@deepseek-ai/dsh-llm',
  '@deepseek-ai/dsh-skill-filesystem',
];

for (const version of [
  '0.1.0-rc.6', '0.1.5-rc.3', '0.1.7-rc.2', '0.2.0-rc.1', '0.2.0',
  // Synthetic future inputs test admission only, not future API compatibility.
  '0.3.0-rc.1', '1.0.0-rc.1', '2.0.0',
]) {
  assert.equal(evaluatePluginCompatibility(manifest, {}, version), undefined, version);
}
for (const version of ['0.0.9', '0.1.0-rc.5']) {
  const issue = evaluatePluginCompatibility(manifest, {}, version);
  assert.ok(issue, `versions below the admission floor must be rejected: ${version}`);
  assert.deepEqual(Object.keys(issue.peers).sort(), [...peers].sort());
  assert.equal(issue.exempted, false);
}

const oldManifest = {
  ...manifest,
  peerDependencies: Object.fromEntries(peers.map(peer => [peer, '^0.1.0-rc.6'])),
};
const oldIssue = evaluatePluginCompatibility(oldManifest, {}, '0.2.0-rc.1');
assert.ok(oldIssue, 'the released manifest must reproduce the reported rejection');
assert.deepEqual(Object.keys(oldIssue.peers).sort(), [...peers].sort());
assert.equal(oldIssue.exempted, false);
assert.equal(evaluatePluginCompatibility(manifest), undefined, 'installed runtime admission');
console.log(`DSH ${getDshRuntimeVersion()}: admission matrix passed; no version exemption used.`);
