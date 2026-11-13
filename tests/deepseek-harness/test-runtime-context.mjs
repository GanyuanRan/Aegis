// Optional real-host check; no provider credentials or live model calls.
// node tests/deepseek-harness/test-runtime-context.mjs <isolated-host-package.json>
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";
import { installBootstrap, BOOTSTRAP_MARKER } from "../../extensions/dsh/bootstrap.js";

if (!process.argv[2]) throw new Error("Provide an isolated DSH installation package.json");
const requireHost = createRequire(path.resolve(process.argv[2]));
const load = (name) => import(pathToFileURL(requireHost.resolve(`@deepseek-ai/${name}`)));
const { Context } = await load("cordis");
const { default: LlmRuntime, LlmAdapter, LlmError, createUserMessage } = await load("dsh-llm");
const { default: SessionStore } = await load("dsh-session");
const { default: SystemPrompt } = await load("dsh-system-prompt");
const { default: Tools } = await load("dsh-tools");
const NativeTools = await load("dsh-tool-executor-native");
const { defineContentToolFixture } = await load("dsh-tool-testkit");
const { default: Agents } = await load("dsh-agent");
const { default: AgentLoop } = await load("dsh-agent-loop");
const { default: Projections } = await load("dsh-session-projection");
const skillsRoot = fileURLToPath(new URL("../../skills/", import.meta.url));
const originalActivation = process.env.AEGIS_ACTIVATION_MODE;
const originalTdd = process.env.AEGIS_TDD_MODE;
process.env.AEGIS_ACTIVATION_MODE = "auto";
process.env.AEGIS_TDD_MODE = "off";
const deadline = setTimeout(() => {
  console.error("FAIL real-host context checks exceeded 30 seconds");
  process.exit(1);
}, 30_000);
deadline.unref();

function response(block = { type: "text", text: "done" }) {
  return [
    { type: "block-start", index: 0, blockType: block.type },
    { type: "block-end", index: 0, block },
    { type: "finish", reason: { kind: block.type === "tool-call" ? "tool-calls" : "stop" } },
  ];
}
class ScriptedAdapter extends LlmAdapter {
  requests = [];
  script = [];
  async resolveModel(provider, model) { return { provider, id: model, name: model }; }
  async *stream(options) {
    this.requests.push(structuredClone(options.messages));
    assert.ok(this.requests.length < 20, "unexpected continuing model steps");
    const next = this.script.shift();
    if (next instanceof Error) throw next;
    for (const chunk of next ?? response()) yield chunk;
  }
}
const containsRouter = (messages) => messages.some((m) =>
  m.role === "user" && m.source?.kind === "runtime-context" &&
  m.content.some((b) => b.type === "text" && b.text.includes(BOOTSTRAP_MARKER)));
const snapshots = (agent) => agent.session.snapshotEvents().filter((e) =>
  e.type === "user/message" && e.data.source.kind === "runtime-context");

let serial = 0;
async function withHost(check, activation = "auto") {
  const ctx = new Context();
  const adapter = new ScriptedAdapter();
  try {
    for (const plugin of [LlmRuntime, SessionStore, Projections, SystemPrompt, Tools, NativeTools, Agents]) {
      await ctx.plugin(plugin);
    }
    await ctx.plugin(AgentLoop, { agents: [] });
    ctx.llm.registerAdapter(["mock"], adapter);
    process.env.AEGIS_ACTIVATION_MODE = activation;
    const dispose = installBootstrap(ctx, { skillsRoot });
    const agent = await ctx.agentLoop.create(`aegis-context-${++serial}`, { provider: "mock", model: "mock" });
    // A regression to inbox injection must fail even if a timing accident hides extra requests.
    agent.inject = () => { throw new Error("Aegis must not inject pending work"); };
    const send = async (text) => {
      agent.followup(createUserMessage({ content: [{ type: "text", text }], source: { kind: "user" } }));
      await agent.whenIdle();
      const end = agent.session.snapshotEvents().findLast((e) => e.type === "turn/end");
      assert.notEqual(end?.data.reason.kind, "error", JSON.stringify(end?.data));
    };
    await check({ ctx, adapter, agent, send, dispose });
  } finally {
    await ctx.fiber.dispose();
  }
}
function replaceContext(agent) {
  const retained = snapshots(agent).at(-1);
  assert.ok(retained, "context was admitted before replacement");
  agent.session.append("user/message", createUserMessage({
    content: [{ type: "text", text: "compacted checkpoint" }], source: { kind: "test-compaction" },
  }), {
    surfaceOp: { op: "replace", startSeq: retained.seq, endSeq: retained.seq },
    sourceEventSeqs: [retained.seq],
  });
}

try {
  await withHost(async ({ ctx, adapter, agent, send, dispose }) => {
    assert.equal(adapter.requests.length, 0, "registration cannot start work");
    await send("first");
    assert.equal(adapter.requests.length, 1, "text-only answer ends its turn");
    assert.ok(containsRouter(adapter.requests[0]), "first request has guidance");
    await send("second");
    assert.equal(adapter.requests.length, 2);
    assert.equal(snapshots(agent).length, 1, "unchanged context is not appended again");
    replaceContext(agent);
    await send("after compaction");
    assert.equal(adapter.requests.length, 3);
    assert.ok(containsRouter(adapter.requests[2]));
    assert.equal(snapshots(agent).length, 2);
    dispose();
    await send("after unload");
    const latest = snapshots(agent).at(-1);
    assert.ok(!JSON.stringify(latest.data).includes(BOOTSTRAP_MARKER), "host supersedes unloaded context");
    installBootstrap(ctx, { skillsRoot });
    await send("after reload");
    assert.equal(adapter.requests.length, 5);
    assert.ok(containsRouter(adapter.requests[4]));
  });
  console.log("PASS text-only turns, retained-context dedup, replacement, unload/reload");

  for (const timing of ["before", "after"]) {
    await withHost(async ({ ctx, adapter, agent, send }) => {
      await send("first");
      ctx.on("agent/pre-step", async (_payload, next) => {
        if (timing === "before") replaceContext(agent);
        const decision = await next();
        if (timing === "after") replaceContext(agent);
        return decision;
      });
      await send("replacement during assembly");
      assert.equal(adapter.requests.length, 2);
      assert.ok(containsRouter(adapter.requests[1]));
    });
  }
  console.log("PASS replacement before and after pre-step admission");

  for (const replace of [false, true]) {
    await withHost(async ({ ctx, adapter, agent, send }) => {
      await send("first");
      adapter.script.push(LlmError.fromFailure({ code: "CONTEXT_LENGTH", message: "scripted retry" }), response());
      ctx.on("agent/request-error", async () => {
        if (replace) replaceContext(agent);
        return { kind: "retry" };
      });
      await send("retry");
      assert.equal(adapter.requests.length, 3);
      assert.ok(containsRouter(adapter.requests[2]));
      assert.equal(snapshots(agent).length, replace ? 2 : 1);
      assert.equal(agent.session.snapshotEvents().filter((e) => e.type === "user/message" && e.data.source.kind === "user").length, 2);
    });
  }
  console.log("PASS retries with and without context replacement");

  await withHost(async ({ ctx, adapter, agent, send }) => {
    const stop = ctx.on("agent/pre-step", async (_payload, next) => {
      const decision = await next();
      agent.cancel({ kind: "user" });
      return decision;
    });
    await send("cancel before admission");
    assert.equal(adapter.requests.length, 0);
    assert.equal(snapshots(agent).length, 0);
    stop();
    await send("later user request");
    assert.equal(adapter.requests.length, 1);
    assert.ok(containsRouter(adapter.requests[0]));
  });
  console.log("PASS cancellation does not consume context or create work");

  await withHost(async ({ ctx, adapter, agent, send }) => {
    ctx.tools.register(defineContentToolFixture({
      name: "echo", description: "Scripted read-only tool", parameters: {},
      async execute() {
        replaceContext(agent);
        return [{ type: "text", text: "tool result" }];
      },
    }));
    adapter.script.push(response({ type: "tool-call", id: "echo-1", name: "echo", arguments: "{}" }), response());
    await send("use a tool");
    assert.equal(adapter.requests.length, 2, "one tool step and one final answer");
    assert.ok(adapter.requests.every(containsRouter), "tool continuation recovers guidance");
    assert.ok(adapter.requests[1].some((m) => m.role === "tool"));
  });
  console.log("PASS tool continuation with context replacement");

  for (const mode of ["explicit", "suppressed"]) {
    await withHost(async ({ ctx, adapter, send }) => {
      if (mode === "suppressed") ctx.systemPrompt.suppressRuntimeContext();
      await send("normal user request");
      assert.equal(adapter.requests.length, 1);
      assert.equal(containsRouter(adapter.requests[0]), false);
    }, mode === "explicit" ? "explicit" : "auto");
  }
  console.log("PASS explicit activation and host suppression");

  await withHost(async ({ ctx, adapter }) => {
    const { agent: child } = await ctx.agentLoop.createAgent(ctx, {
      sessionId: `aegis-child-${++serial}`,
      meta: { origin: "subagent" },
      agentOptions: { provider: "mock", model: "mock" },
    });
    child.followup(createUserMessage({ content: [{ type: "text", text: "delegated work" }], source: { kind: "user" } }));
    await child.whenIdle();
    assert.equal(adapter.requests.length, 1);
    assert.equal(containsRouter(adapter.requests[0]), false);
    assert.equal(snapshots(child).length, 0);
  });
  console.log("PASS real subagent exclusion");
} finally {
  clearTimeout(deadline);
  for (const [name, value] of [["AEGIS_ACTIVATION_MODE", originalActivation], ["AEGIS_TDD_MODE", originalTdd]]) {
    if (value === undefined) delete process.env[name]; else process.env[name] = value;
  }
}
