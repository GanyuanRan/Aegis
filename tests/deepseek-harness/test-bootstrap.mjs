import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  BOOTSTRAP_MARKER,
  buildBootstrap,
  installBootstrap,
  readAegisConfig,
  readUsingAegisBody,
  stripFrontmatter,
} from "../../extensions/dsh/bootstrap.js";

const repoRoot = fileURLToPath(new URL("../../", import.meta.url));
const skillsRoot = path.join(repoRoot, "skills");
const tempRoot = fs.mkdtempSync(path.join(os.tmpdir(), "aegis-dsh-bootstrap-"));
const originalActivation = process.env.AEGIS_ACTIVATION_MODE;
const originalTdd = process.env.AEGIS_TDD_MODE;

function restoreEnv(name, value) {
  if (value === undefined) delete process.env[name];
  else process.env[name] = value;
}

function fakeContext() {
  const contributions = new Map();
  return {
    contributions,
    systemPrompt: {
      context(entry) {
        assert.equal(contributions.has(entry.name), false);
        contributions.set(entry.name, entry);
        return () => contributions.delete(entry.name);
      },
    },
    on() { throw new Error("Bootstrap must not subscribe to scheduling events"); },
  };
}

try {
  delete process.env.AEGIS_ACTIVATION_MODE;
  delete process.env.AEGIS_TDD_MODE;

  const body = readUsingAegisBody(skillsRoot);
  assert.match(body, /<EXTREMELY-IMPORTANT>/);
  assert.doesNotMatch(body, /^---/);

  // The frontmatter-strip contract is pinned directly, not only indirectly
  // through the real skill body.
  assert.equal(
    stripFrontmatter("---\nname: synthetic\n---\nBODY-CONTENT\n"),
    "BODY-CONTENT\n",
  );
  assert.equal(stripFrontmatter("NO-FRONTMATTER\n"), "NO-FRONTMATTER\n");

  // A missing using-aegis skill body fails loudly at plugin apply time
  // rather than silently arming an empty bootstrap.
  assert.throws(
    () => readUsingAegisBody(path.join(tempRoot, "missing-skills")),
    /Aegis DSH bootstrap skill is missing/,
  );

  const rendered = buildBootstrap(body, { tddMode: "off" });
  assert.match(rendered, new RegExp(`<${BOOTSTRAP_MARKER}>`));
  assert.match(rendered, /native `skill` tool/);
  assert.match(rendered, /Route: fast-path/);
  assert.doesNotMatch(rendered, /routing-guard marker/i);

  // The auto branch of the TDD mode line is a distinct render path of the
  // repaired owner; pin it so both tddMode branches stay covered.
  const renderedAuto = buildBootstrap(body, { tddMode: "auto" });
  assert.match(renderedAuto, new RegExp(`<${BOOTSTRAP_MARKER}>`));
  assert.match(renderedAuto, /Aegis TDD mode: auto\./);
  assert.doesNotMatch(renderedAuto, /Aegis TDD mode: off\./);

  const autoCtx = fakeContext();
  const disposer = installBootstrap(autoCtx, { skillsRoot, homeDir: tempRoot });
  assert.equal(typeof disposer, "function");
  assert.equal(autoCtx.contributions.size, 1);
  const entry = autoCtx.contributions.get("aegis-routing");
  assert.equal(entry.interpolate, false);
  assert.equal(Number.isFinite(entry.order), true);
  const agent = {
    session: { header: {} },
    inject() { throw new Error("Advisory context must never enqueue work"); },
  };
  assert.equal(entry.text({ agent }), rendered);
  assert.equal(entry.text({ agent }), rendered, "provider has no delivery side effects");
  assert.equal(entry.text({}), "", "non-agent assemblies get no routing context");
  assert.equal(entry.text({ agent: { session: { header: { origin: "subagent" } } } }), "");
  const cancelled = new AbortController();
  cancelled.abort();
  assert.equal(entry.text({ agent, signal: cancelled.signal }), "");
  assert.equal(entry.text({ agent }), rendered, "cancelled assembly does not consume guidance");
  disposer();
  assert.equal(autoCtx.contributions.size, 0);
  const disposeReloaded = installBootstrap(autoCtx, { skillsRoot, homeDir: tempRoot });
  assert.equal(autoCtx.contributions.size, 1);
  disposeReloaded();

  const explicitHome = path.join(tempRoot, "explicit-home");
  fs.mkdirSync(path.join(explicitHome, ".config", "aegis"), { recursive: true });
  fs.writeFileSync(
    path.join(explicitHome, ".config", "aegis", "config.toml"),
    'activation_mode = "explicit"\ntdd_mode = "auto"\n',
    "utf8",
  );
  assert.deepEqual(readAegisConfig(explicitHome), {
    activationMode: "explicit",
    tddMode: "auto",
  });
  const explicitCtx = fakeContext();
  assert.equal(
    installBootstrap(explicitCtx, {
      skillsRoot,
      homeDir: explicitHome,
    }),
    null,
  );
  assert.equal(explicitCtx.contributions.size, 0);

  process.env.AEGIS_ACTIVATION_MODE = "auto";
  process.env.AEGIS_TDD_MODE = "off";
  assert.deepEqual(readAegisConfig(explicitHome), {
    activationMode: "auto",
    tddMode: "off",
  });

  process.env.AEGIS_ACTIVATION_MODE = "invalid";
  process.env.AEGIS_TDD_MODE = "invalid";
  assert.deepEqual(readAegisConfig(explicitHome), {
    activationMode: "auto",
    tddMode: "off",
  });

  console.log("DeepSeek Harness bootstrap checks passed.");
} finally {
  restoreEnv("AEGIS_ACTIVATION_MODE", originalActivation);
  restoreEnv("AEGIS_TDD_MODE", originalTdd);
  fs.rmSync(tempRoot, { recursive: true, force: true });
}
