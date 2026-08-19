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

function fakeAgent(id, origin) {
  const injected = [];
  const session = { header: origin ? { origin } : {} };
  if (id !== undefined) session.id = id;
  return {
    injected,
    session,
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

  const eventHandler = autoCtx.handlers.get("session/event");
  assert.equal(typeof eventHandler, "function");

  // Every session-start boundary arms the deferral; nothing is injected
  // before the session's first durable promotion signal, so the first model
  // request stays free of Aegis content.
  const coordinator = fakeAgent("session-1");
  for (const source of ["startup", "resume", "clear", "compact"]) {
    const returned = lifecycleHandler({ agent: coordinator, source });
    assert.equal(returned, undefined, `${source} must arm, not inject`);
    eventHandler(coordinator.session, { type: "user/message" });
    assert.equal(coordinator.injected.length, 0, `${source} must not inject on non-promotion events`);
  }

  // The first durable promotion signal releases exactly one injection.
  eventHandler(coordinator.session, { type: "assistant/message" });
  assert.equal(coordinator.injected.length, 1);
  const message = coordinator.injected[0];
  assert.equal(message.role, "user");
  assert.deepEqual(message.source, {
    kind: "plugin",
    plugin: "aegis",
    form: "instructions",
  });
  assert.match(message.content[0].text, new RegExp(BOOTSTRAP_MARKER));

  // Later promotion signals never double-inject.
  eventHandler(coordinator.session, { type: "tool/call" });
  assert.equal(coordinator.injected.length, 1);

  // A compaction boundary re-arms the deferral: the first post-compaction
  // request is a gated "second first request", so only a NEW promotion
  // signal may inject again.
  eventHandler(coordinator.session, { type: "compaction/end" });
  eventHandler(coordinator.session, { type: "user/message" });
  assert.equal(coordinator.injected.length, 1, "compaction re-arm must not inject on non-promotion events");
  eventHandler(coordinator.session, { type: "tool/call" });
  assert.equal(coordinator.injected.length, 2);
  assert.match(coordinator.injected[1].content[0].text, new RegExp(BOOTSTRAP_MARKER));

  // A mid-session session-start with source "clear" re-arms the deferral
  // exactly like compaction: the cleared session's next first request is
  // again a gated first request, so only a promotion signal may inject.
  lifecycleHandler({ agent: coordinator, source: "clear" });
  eventHandler(coordinator.session, { type: "user/message" });
  assert.equal(
    coordinator.injected.length,
    2,
    "clear re-arm must not inject on non-promotion events",
  );
  eventHandler(coordinator.session, { type: "assistant/message" });
  assert.equal(coordinator.injected.length, 3);
  assert.match(coordinator.injected[2].content[0].text, new RegExp(BOOTSTRAP_MARKER));

  // Other sessions' events never inject into this session, and sessions
  // never seen at session-start are ignored entirely.
  const stranger = fakeAgent("session-2");
  eventHandler(stranger.session, { type: "tool/call" });
  assert.equal(stranger.injected.length, 0);

  // Subagents are excluded from lifecycle arming.
  const subagent = fakeAgent("session-3", "subagent");
  lifecycleHandler({ agent: subagent, source: "startup" });
  eventHandler(subagent.session, { type: "tool/call" });
  assert.equal(subagent.injected.length, 0);

  // Sessions without a stable session.id cannot be correlated with their
  // events, so they are skipped rather than injected blind.
  const idless = fakeAgent(undefined);
  lifecycleHandler({ agent: idless, source: "startup" });
  eventHandler(idless.session, { type: "tool/call" });
  assert.equal(idless.injected.length, 0);

  // Disposal tears down both listeners; the host no longer dispatches to
  // them, so no new session can arm or receive an injection.
  disposer();
  assert.equal(autoCtx.handlers.has("agent/session-start"), false);
  assert.equal(autoCtx.handlers.has("session/event"), false);

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
