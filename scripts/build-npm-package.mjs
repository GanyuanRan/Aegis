import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../", import.meta.url));
const npmCli = process.env.npm_execpath ?? (process.platform === "win32"
  ? path.resolve(path.dirname(process.execPath), "node_modules/npm/bin/npm-cli.js")
  : fs.realpathSync(execFileSync("which", ["npm"], { encoding: "utf8" }).trim()));

export function runNpm(args, cwd = root) {
  return execFileSync(process.execPath, [npmCli, ...args], {
    cwd, encoding: "utf8", maxBuffer: 16 * 1024 * 1024,
  });
}

export function buildNpmPackage(outputDirectory) {
  const output = path.resolve(outputDirectory);
  fs.mkdirSync(output, { recursive: true });
  const stage = fs.mkdtempSync(path.join(os.tmpdir(), "aegis-npm-package-"));
  try {
    const manifest = JSON.parse(fs.readFileSync(path.join(root, "package.json"), "utf8"));
    const sourceName = manifest.name;
    const packageName = "aegis-method-pack";
    const includes = [
      "skills", "scripts", "extensions", "docs", "assets", "commands", "hooks",
      ".opencode", ".claude-plugin", ".codebuddy-plugin", ".codex-plugin", ".codex",
      ".cursor-plugin", ".cursor", ".windsurf", ".github/skills", ".github/hooks",
      ".github/copilot-instructions.md", "kimi.plugin.json", "AGENTS.md", "CLAUDE.md",
      "CONTEXT.md", "GLOBAL_USER_RULES_TEMPLATE.md", "GLOBAL_USER_RULES_TEMPLATE.zh-CN.md",
      "README.md", "README.en.md", "README.zh-CN.md", "RELEASE-NOTES.md", "LICENSE",
      "CONTRIBUTING.md", "SECURITY.md", "SUPPORT.md",
    ];
    const publicFiles = execFileSync("git", ["ls-files", "-z"], {
      cwd: root, encoding: "utf8",
    }).split("\0").filter(Boolean);
    publicFiles.push("scripts/build-npm-package.mjs");
    for (const file of new Set(publicFiles)) {
      if (!includes.some((entry) => file === entry || file.startsWith(`${entry}/`))) continue;
      const source = path.join(root, file);
      const sourceRelative = path.relative(fs.realpathSync(root), fs.realpathSync(source));
      assert.ok(!sourceRelative.startsWith("..") && !path.isAbsolute(sourceRelative), file);
      const destination = path.join(stage, file);
      fs.mkdirSync(path.dirname(destination), { recursive: true });
      fs.copyFileSync(source, destination);
    }
    manifest.name = packageName;
    delete manifest.private;
    // Source-only commands require a Git checkout and excluded test files.
    delete manifest.scripts;
    manifest.files = includes;
    const patchPath = path.join(stage, manifest.dsh.bundle.patch);
    const patch = fs.readFileSync(patchPath, "utf8");
    const sourceEntry = `${sourceName}/extensions/dsh/index.js`;
    assert.equal(patch.split(sourceEntry).length, 2, "one canonical DSH entry is required");
    fs.writeFileSync(patchPath, patch.replace(sourceEntry, `${packageName}/extensions/dsh/index.js`));
    fs.writeFileSync(path.join(stage, "package.json"), JSON.stringify(manifest, null, 2) + "\n");
    const [packed] = JSON.parse(runNpm([
      "pack", "--json", "--ignore-scripts", "--pack-destination", output,
    ], stage));
    assert.equal(packed.name, packageName);
    assert.equal(packed.version, manifest.version);
    const { files: _files, ...artifact } = packed;
    return { ...artifact, path: path.join(output, packed.filename) };
  } finally {
    assert.equal(path.dirname(path.resolve(stage)), path.resolve(os.tmpdir()));
    assert.ok(path.basename(stage).startsWith("aegis-npm-package-"));
    fs.rmSync(stage, { recursive: true, force: true });
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2);
  assert.ok(args.length === 0 || (args.length === 2 && args[0] === "--output"),
    "Usage: node scripts/build-npm-package.mjs [--output <directory>]");
  console.log(JSON.stringify(buildNpmPackage(args[1] ?? path.join(root, ".tmp/npm-release"))));
}
