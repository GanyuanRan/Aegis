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

function waitForDeferredDelivery() {
  // Bootstrap delivery intentionally crosses one timer boundary so it runs
  // after the host's synchronous session-event publication has unwound.
  return new Promise((resolve) => setTimeout(resolve, 0));
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
  assert.equal(coordinator.injected.length, 0);
  await waitForDeferredDelivery();
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
  assert.equal(coordinator.injected.length, 1);
  await waitForDeferredDelivery();
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
  assert.equal(coordinator.injected.length, 2);
  await waitForDeferredDelivery();
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

  // Event-handler correlation guards: an event session without a stable id
  // is ignored entirely, and compaction/end for a session never seen at
  // session-start never arms an injection for it.
  eventHandler({ id: undefined }, { type: "tool/call" });
  eventHandler({ id: undefined }, { type: "compaction/end" });
  const strangerCompact = fakeAgent("session-4");
  eventHandler(strangerCompact.session, { type: "compaction/end" });
  eventHandler(strangerCompact.session, { type: "tool/call" });
  assert.equal(strangerCompact.injected.length, 0);

  // The real DSH session store rejects agent.inject while a session/event is
  // still being published. Delivery must cross the publish-stack boundary.
  const reentrantCtx = fakeContext();
  const disposeReentrant = installBootstrap(reentrantCtx, {
    createUserMessage: fakeCreateUserMessage,
    skillsRoot,
    homeDir: tempRoot,
  });
  const reentrantLifecycle = reentrantCtx.handlers.get("agent/session-start");
  const reentrantEvent = reentrantCtx.handlers.get("session/event");
  let publishInFlight = false;
  const reentrantAgent = fakeAgent("session-reentrant");
  reentrantAgent.inject = (injectedMessage) => {
    assert.equal(
      publishInFlight,
      false,
      "bootstrap injection must not re-enter session/event publication",
    );
    reentrantAgent.injected.push(injectedMessage);
  };
  reentrantLifecycle({ agent: reentrantAgent, source: "startup" });
  publishInFlight = true;
  try {
    reentrantEvent(reentrantAgent.session, { type: "tool/call" });
  } finally {
    publishInFlight = false;
  }
  assert.equal(reentrantAgent.injected.length, 0);
  await waitForDeferredDelivery();
  assert.equal(reentrantAgent.injected.length, 1);

  // Later promotion events do not schedule duplicate delivery after the
  // armed epoch has already been released.
  reentrantEvent(reentrantAgent.session, { type: "assistant/message" });
  await waitForDeferredDelivery();
  assert.equal(reentrantAgent.injected.length, 1);

  // A lifecycle re-arm invalidates delivery queued for the prior epoch. The
  // newly armed epoch must wait for its own durable promotion signal.
  reentrantLifecycle({ agent: reentrantAgent, source: "resume" });
  reentrantEvent(reentrantAgent.session, { type: "tool/call" });
  reentrantLifecycle({ agent: reentrantAgent, source: "clear" });
  await waitForDeferredDelivery();
  assert.equal(reentrantAgent.injected.length, 1);
  reentrantEvent(reentrantAgent.session, { type: "assistant/message" });
  await waitForDeferredDelivery();
  assert.equal(reentrantAgent.injected.length, 2);

  // A compaction boundary has the same invalidation rule even though it is
  // observed on session/event rather than agent/session-start.
  reentrantLifecycle({ agent: reentrantAgent, source: "resume" });
  reentrantEvent(reentrantAgent.session, { type: "assistant/message" });
  reentrantEvent(reentrantAgent.session, { type: "compaction/end" });
  await waitForDeferredDelivery();
  assert.equal(reentrantAgent.injected.length, 2);
  reentrantEvent(reentrantAgent.session, { type: "tool/call" });
  await waitForDeferredDelivery();
  assert.equal(reentrantAgent.injected.length, 3);
  disposeReentrant();

  // Exact agent disposal cancels pending delivery, removes retained state,
  // and allows a later agent with the same session id to own a fresh epoch.
  const agentDisposalCtx = fakeContext();
  const disposeAgentDisposal = installBootstrap(agentDisposalCtx, {
    createUserMessage: fakeCreateUserMessage,
    skillsRoot,
    homeDir: tempRoot,
  });
  const agentDisposalLifecycle = agentDisposalCtx.handlers.get("agent/session-start");
  const agentDisposalEvent = agentDisposalCtx.handlers.get("session/event");
  const agentDisposed = agentDisposalCtx.handlers.get("agent/disposed");
  assert.equal(typeof agentDisposed, "function");
  const departedAgent = fakeAgent("session-reused");
  agentDisposalLifecycle({ agent: departedAgent, source: "startup" });
  agentDisposalEvent(departedAgent.session, { type: "tool/call" });
  agentDisposed({ agent: departedAgent });
  await waitForDeferredDelivery();
  assert.equal(departedAgent.injected.length, 0);

  const replacementAgent = fakeAgent("session-reused");
  agentDisposalLifecycle({ agent: replacementAgent, source: "resume" });
  agentDisposed({ agent: departedAgent });
  agentDisposalEvent(replacementAgent.session, { type: "assistant/message" });
  await waitForDeferredDelivery();
  assert.equal(replacementAgent.injected.length, 1);
  disposeAgentDisposal();

  // Disposal cancels a delivery that was scheduled but has not run yet.
  const disposalCtx = fakeContext();
  const disposeBeforeDelivery = installBootstrap(disposalCtx, {
    createUserMessage: fakeCreateUserMessage,
    skillsRoot,
    homeDir: tempRoot,
  });
  const disposalAgent = fakeAgent("session-disposal");
  disposalCtx.handlers.get("agent/session-start")({
    agent: disposalAgent,
    source: "startup",
  });
  disposalCtx.handlers.get("session/event")(disposalAgent.session, {
    type: "tool/call",
  });
  disposeBeforeDelivery();
  await waitForDeferredDelivery();
  assert.equal(disposalAgent.injected.length, 0);

  // Deferred failures are visible rather than becoming unhandled timer
  // exceptions or silent missing bootstrap messages.
  const failureCtx = fakeContext();
  const disposeFailure = installBootstrap(failureCtx, {
    createUserMessage: fakeCreateUserMessage,
    skillsRoot,
    homeDir: tempRoot,
  });
  const failureAgent = fakeAgent("session-failure");
  failureAgent.inject = () => {
    throw new Error("synthetic injection failure");
  };
  const originalConsoleError = console.error;
  const injectionErrors = [];
  console.error = (...args) => injectionErrors.push(args);
  try {
    failureCtx.handlers.get("agent/session-start")({
      agent: failureAgent,
      source: "startup",
    });
    failureCtx.handlers.get("session/event")(failureAgent.session, {
      type: "assistant/message",
    });
    await waitForDeferredDelivery();
  } finally {
    console.error = originalConsoleError;
    disposeFailure();
  }
  assert.equal(injectionErrors.length, 1);
  assert.match(
    String(injectionErrors[0][0]),
    /deferred bootstrap injection failed/,
  );

  // Disposal tears down both listeners; the host no longer dispatches to
  // them, so no new session can arm or receive an injection.
  disposer();
  assert.equal(autoCtx.handlers.has("agent/session-start"), false);
  assert.equal(autoCtx.handlers.has("agent/disposed"), false);
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
