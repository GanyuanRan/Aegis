// Exercise the published host's native provider against an installed artifact.
// No model request, Desktop UI, or full application bootstrap is implied.
import assert from 'node:assert/strict';
import { readdir, readFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { resolve, join } from 'node:path';
import { pathToFileURL } from 'node:url';

if (process.argv.length !== 4) {
  throw new Error('Usage: node test-installed-skills.mjs <host-package.json> <installed-package-root>');
}
const host = createRequire(resolve(process.argv[2]));
const { FileSystemSkillProvider } = await import(pathToFileURL(host.resolve('@deepseek-ai/dsh-skill-filesystem')));
const skillsRoot = resolve(process.argv[3], 'skills');
const expected = (await readdir(skillsRoot, { withFileTypes: true }))
  .filter(entry => entry.isDirectory()).map(entry => entry.name).sort();
assert.ok(expected.includes('using-aegis'));
const warnings = [];
const provider = new FileSystemSkillProvider({
  get: () => undefined,
  logger: { warn: message => warnings.push(message) },
}, { signal: new AbortController().signal, invalidate() {} }, {
  providerName: 'aegis-method-pack', includeDefaultRoots: false,
  bundledSkillDir: skillsRoot, watch: false,
});
try {
  const candidates = await provider.list({});
  assert.ok(Array.isArray(candidates), 'Native discovery must be complete');
  assert.deepEqual(candidates.map(candidate => candidate.name).sort(), expected);
  for (const candidate of candidates) {
    const loaded = await provider.get(candidate, {});
    assert.equal(loaded.name, candidate.name);
    assert.ok(loaded.content.trim().length > 0);
    const source = await readFile(join(skillsRoot, candidate.name, 'SKILL.md'), 'utf8');
    assert.ok(source.replaceAll('\r\n', '\n').includes(loaded.content.replaceAll('\r\n', '\n').trim()));
  }
  assert.deepEqual(warnings, []);
  console.log(`Native filesystem provider discovered and loaded ${candidates.length} installed skills.`);
} finally {
  await provider.dispose();
}
