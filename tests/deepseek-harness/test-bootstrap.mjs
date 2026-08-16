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

function fakeCreateUserMessage(input) {
  return { id: "aegis-test-message", role: "user", ...input };
}

function fakeContext() {
  const handlers = new Map();
  return {
    handlers,
    on(name, handler) {
      handlers.set(name, handler);
      return () => handlers.delete(name);
    },
  };
}

function fakeAgent(origin) {
  const injected = [];
  return {
    injected,
    session: { header: origin ? { origin } : {} },
    inject(message) {
      injected.push(message);
    },
  };
}

try {
  delete process.env.AEGIS_ACTIVATION_MODE;
  delete process.env.AEGIS_TDD_MODE;

  const body = readUsingAegisBody(skillsRoot);
  assert.match(body, /<EXTREMELY-IMPORTANT>/);
  assert.doesNotMatch(body, /^---/);

  const rendered = buildBootstrap(body, { tddMode: "off" });
  assert.match(rendered, new RegExp(`<${BOOTSTRAP_MARKER}>`));
  assert.match(rendered, /native `skill` tool/);
  assert.match(rendered, /Route: fast-path/);
  assert.doesNotMatch(rendered, /routing-guard marker/i);

  const autoCtx = fakeContext();
  const disposer = installBootstrap(autoCtx, {
    createUserMessage: fakeCreateUserMessage,
    skillsRoot,
    homeDir: tempRoot,
  });
  assert.equal(typeof disposer, "function");
  const lifecycleHandler = autoCtx.handlers.get("agent/session-start");
  assert.equal(typeof lifecycleHandler, "function");

  const coordinator = fakeAgent();
  for (const source of ["startup", "resume", "clear", "compact"]) {
    const returned = lifecycleHandler({ agent: coordinator, source });
    assert.equal(returned, undefined, `${source} injection must stay synchronous`);
  }
  assert.equal(coordinator.injected.length, 4);
  for (const message of coordinator.injected) {
    assert.equal(message.role, "user");
    assert.deepEqual(message.source, {
      kind: "plugin",
      plugin: "aegis",
      form: "instructions",
    });
    assert.match(message.content[0].text, new RegExp(BOOTSTRAP_MARKER));
  }

  const subagent = fakeAgent("subagent");
  lifecycleHandler({ agent: subagent, source: "startup" });
  assert.equal(subagent.injected.length, 0);

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
      createUserMessage: fakeCreateUserMessage,
      skillsRoot,
      homeDir: explicitHome,
    }),
    null,
  );
  assert.equal(explicitCtx.handlers.size, 0);

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
