import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { buildNpmPackage, runNpm } from "../../scripts/build-npm-package.mjs";

const root = fileURLToPath(new URL("../../", import.meta.url));
const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "aegis-npm-test-"));
try {
  const originalManifest = fs.readFileSync(path.join(root, "package.json"), "utf8");
  const originalPatch = fs.readFileSync(path.join(root, "extensions/dsh/cordis.patch.yml"), "utf8");
  const source = JSON.parse(originalManifest);
  const args = process.argv.slice(2);
  assert.ok(args.length === 0 || (args.length === 2 && args[0] === "--artifact"),
    "Usage: node tests/deepseek-harness/test-npm-package.mjs [--artifact <tarball>]");
  const artifact = args.length ? { path: path.resolve(args[1]) } : buildNpmPackage(temporary);
  fs.copyFileSync(artifact.path, path.join(temporary, "artifact.tgz"));
  const extraction = path.join(temporary, "extracted");
  fs.mkdirSync(extraction);
  // A relative archive path also works with Git Bash's GNU tar on Windows:
  // it otherwise interprets the drive-letter colon as a remote archive.
  execFileSync("tar", ["-xzf", "artifact.tgz", "-C", "extracted"], {
    cwd: temporary,
  });
  const packaged = path.join(extraction, "package");
  const manifest = JSON.parse(fs.readFileSync(path.join(packaged, "package.json"), "utf8"));
  assert.equal(manifest.name, "aegis-method-pack");
  assert.equal(manifest.version, source.version);
  assert.equal(manifest.private, undefined);
  assert.equal(manifest.scripts, undefined, "source-only npm scripts must not ship");
  assert.deepEqual(manifest.peerDependencies, source.peerDependencies);
  assert.deepEqual(manifest.peerDependenciesMeta, source.peerDependenciesMeta);
  assert.equal(manifest.repository.url, "git+https://github.com/GanyuanRan/Aegis.git");
  assert.match(fs.readFileSync(path.join(packaged, manifest.dsh.bundle.patch), "utf8"),
    /name: 'aegis-method-pack\/extensions\/dsh\/index\.js'/);
  const required = [
    manifest.main, "extensions/dsh/index.js", "extensions/dsh/bootstrap.js",
    "scripts/aegis-doctor.py", "scripts/aegis-workspace.py", "LICENSE",
    "skills/using-aegis/SKILL.md", "skills/long-task-continuation/durable-work-guidance.md",
    ".claude-plugin/plugin.json", ".codebuddy-plugin/plugin.json",
    ".codex-plugin/plugin.json", ".cursor-plugin/plugin.json", "kimi.plugin.json",
  ];
  for (const file of required) assert.ok(fs.existsSync(path.join(packaged, file)), file);
  for (const directory of ["skills", "extensions", "scripts"]) {
    for (const file of fs.readdirSync(path.join(root, directory), { recursive: true })) {
      const relative = path.join(directory, file);
      if (!fs.statSync(path.join(root, relative)).isFile() || relative.includes("__pycache__")
          || relative.endsWith(".pyc")) continue;
      assert.ok(fs.existsSync(path.join(packaged, relative)), relative);
      // The only transformed runtime file is the package-qualified patch.
      if (relative.split(path.sep).join("/") !== "extensions/dsh/cordis.patch.yml") {
        assert.deepEqual(fs.readFileSync(path.join(packaged, relative)),
          fs.readFileSync(path.join(root, relative)), relative);
      }
    }
  }
  for (const excluded of ["docs/archive", "docs/aegis", ".git", "node_modules", "tests", ".tmp"]) {
    assert.equal(fs.existsSync(path.join(packaged, excluded)), false, excluded);
  }
  const install = path.join(temporary, "installed");
  fs.mkdirSync(install);
  fs.writeFileSync(path.join(install, "package.json"), '{"private":true}\n');
  runNpm(["install", "--ignore-scripts", "--omit=optional", "--no-audit", "--no-fund", artifact.path], install);
  const installed = path.join(install, "node_modules/aegis-method-pack");
  assert.ok(fs.existsSync(path.join(installed, "extensions/dsh/index.js")));
  assert.ok(fs.existsSync(path.join(installed, manifest.main)));
  const dependency = JSON.parse(fs.readFileSync(path.join(install, "package.json"), "utf8"));
  assert.ok(dependency.dependencies[manifest.name]);
  assert.equal(fs.readFileSync(path.join(root, "package.json"), "utf8"), originalManifest);
  assert.equal(fs.readFileSync(path.join(root, "extensions/dsh/cordis.patch.yml"), "utf8"), originalPatch);
  console.log(`npm artifact ${manifest.name}@${manifest.version}: identity, full runtime tree, install and Git-source preservation passed`);
} finally {
  assert.equal(path.dirname(path.resolve(temporary)), path.resolve(os.tmpdir()));
  assert.ok(path.basename(temporary).startsWith("aegis-npm-test-"));
  fs.rmSync(temporary, { recursive: true, force: true });
}
