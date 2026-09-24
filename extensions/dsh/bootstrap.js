import fs from "node:fs";
import os from "node:os";
import path from "node:path";

export const BOOTSTRAP_MARKER = "AEGIS_DSH_ROUTING_BOOTSTRAP";

const FRONTMATTER_RE = /^---\s*\r?\n[\s\S]*?\r?\n---\s*\r?\n([\s\S]*)$/;

export function readConfigValue(homeDir, key) {
  try {
    const configPath = path.join(homeDir, ".config", "aegis", "config.toml");
    if (!fs.existsSync(configPath)) return null;

    let value = null;
    for (const line of fs.readFileSync(configPath, "utf8").split(/\r?\n/)) {
      const match = line.match(new RegExp(`^\\s*${key}\\s*=\\s*([^#]+)`));
      if (match) value = match[1].trim().replace(/^["']|["']$/g, "");
    }
    return value;
  } catch {
    return null;
  }
}

export function readAegisConfig(homeDir = os.homedir()) {
  const envActivation = process.env.AEGIS_ACTIVATION_MODE;
  const configuredActivation = readConfigValue(homeDir, "activation_mode");
  const requestedActivation = envActivation ?? configuredActivation;
  const activationMode =
    requestedActivation === "auto" || requestedActivation === "explicit"
      ? requestedActivation
      : "auto";

  const envTdd = process.env.AEGIS_TDD_MODE;
  const configuredTdd = readConfigValue(homeDir, "tdd_mode");
  const requestedTdd = envTdd ?? configuredTdd;
  const tddMode =
    requestedTdd === "auto" || requestedTdd === "off" ? requestedTdd : "off";

  return { activationMode, tddMode };
}

export function stripFrontmatter(content) {
  const normalized = content.replace(/\r\n/g, "\n");
  const match = normalized.match(FRONTMATTER_RE);
  return match ? match[1] : normalized;
}

export function readUsingAegisBody(skillsRoot) {
  const skillPath = path.join(skillsRoot, "using-aegis", "SKILL.md");
  if (!fs.existsSync(skillPath)) {
    throw new Error(`Aegis DSH bootstrap skill is missing: ${skillPath}`);
  }
  return stripFrontmatter(fs.readFileSync(skillPath, "utf8"));
}

export function buildBootstrap(body, { tddMode }) {
  return `<${BOOTSTRAP_MARKER}>
You have Aegis.

Aegis TDD mode: ${tddMode}. off is the default and disables automatic TDD while verification-before-completion still applies; auto routes strict TDD only when risk warrants.

**ROUTING CONTRACT (this lifecycle):** Before the first non-readonly tool call, either use DeepSeek Harness's native \`skill\` tool to load the relevant task-specific Aegis skill, or explicitly declare \`Route: fast-path\` with a one-line reason. The compact \`using-aegis\` hot path is already loaded below; do not load it again.

${body.trim()}

**Tool Mapping for DeepSeek Harness:**
- \`Skill\` tool → DeepSeek Harness's native \`skill\` tool
- \`Read\`, \`Write\`, \`Edit\`, and shell references → the equivalent tools available in the active DSH profile
</${BOOTSTRAP_MARKER}>`;
}

export function createBootstrapMessage(createUserMessage, bootstrap) {
  return createUserMessage({
    content: [{ type: "text", text: bootstrap }],
    source: {
      // DSH session format v4 requires a producer-owned source kind; the bare
      // "plugin" wrapper and its "plugin" field were retired in 0.1.7-rc.1.
      kind: "plugin:aegis",
      form: "instructions",
    },
  });
}

export function installBootstrap(
  ctx,
  { createUserMessage, skillsRoot, homeDir = os.homedir() },
) {
  const config = readAegisConfig(homeDir);
  if (config.activationMode === "explicit") return null;

  // `agent/session-start` is a notification rather than an awaited gate. Read
  // and render synchronously during plugin apply so injection cannot race the
  // first model step.
  const body = readUsingAegisBody(skillsRoot);
  const bootstrap = buildBootstrap(body, config);

  // Injecting at session start used to land the bootstrap in the session
  // inbox BEFORE the first model request, which polluted the sterile
  // first-request baseline that trajectory presets such as
  // dsh-anchored-standard (context gate) depend on. Deferral keeps that
  // request clean: every session-start boundary only ARMS an injection, and
  // the bootstrap lands once the session emits its first durable promotion
  // signal (`tool/call` or `assistant/message`) — after the anchored first
  // request has already been assembled. `compaction/end` re-arms the
  // deferral because the first post-compaction request is itself a gated
  // "second first request". Sessions without a stable `session.id` cannot
  // be correlated with their events, so they are skipped rather than
  // injected blind.
  const agents = new Map();
  const epochs = new Map();
  const pending = new Set();
  const scheduledDeliveries = new Map();
  let disposed = false;

  const reportDeliveryFailure = (error) => {
    console.error("[aegis] deferred bootstrap injection failed:", error);
  };

  const cancelDelivery = (sessionId) => {
    const delivery = scheduledDeliveries.get(sessionId);
    if (delivery === undefined) return;
    clearTimeout(delivery.timer);
    scheduledDeliveries.delete(sessionId);
  };

  const armDelivery = (sessionId, agent) => {
    cancelDelivery(sessionId);
    if (agent !== undefined) agents.set(sessionId, agent);
    epochs.set(sessionId, (epochs.get(sessionId) ?? 0) + 1);
    pending.add(sessionId);
  };

  const deferDelivery = (sessionId, agent, epoch, message) => {
    const delivery = { agent, epoch, timer: undefined };
    delivery.timer = setTimeout(() => {
      if (scheduledDeliveries.get(sessionId) !== delivery) return;
      scheduledDeliveries.delete(sessionId);
      if (
        disposed ||
        agents.get(sessionId) !== agent ||
        epochs.get(sessionId) !== epoch
      ) {
        return;
      }
      try {
        agent.inject(message);
      } catch (error) {
        reportDeliveryFailure(error);
      }
    }, 0);
    scheduledDeliveries.set(sessionId, delivery);
  };

  const disposeLifecycle = ctx.on("agent/session-start", ({ agent }) => {
    if (agent.session?.header?.origin === "subagent") return;
    const sessionId = agent.session?.id;
    if (sessionId === undefined) return;
    armDelivery(sessionId, agent);
  });

  const disposeAgents = ctx.on("agent/disposed", ({ agent }) => {
    const sessionId = agent.session?.id;
    if (sessionId === undefined || agents.get(sessionId) !== agent) return;
    cancelDelivery(sessionId);
    agents.delete(sessionId);
    epochs.delete(sessionId);
    pending.delete(sessionId);
  });

  const disposeEvents = ctx.on("session/event", (session, event) => {
    const sessionId = session?.id;
    if (sessionId === undefined || !agents.has(sessionId)) return;
    if (event?.type === "compaction/end") {
      armDelivery(sessionId);
      return;
    }
    if (event?.type !== "tool/call" && event?.type !== "assistant/message") {
      return;
    }
    if (!pending.delete(sessionId)) return;
    const agent = agents.get(sessionId);
    const epoch = epochs.get(sessionId);
    const message = createBootstrapMessage(createUserMessage, bootstrap);
    deferDelivery(sessionId, agent, epoch, message);
  });

  return () => {
    disposed = true;
    for (const delivery of scheduledDeliveries.values()) {
      clearTimeout(delivery.timer);
    }
    scheduledDeliveries.clear();
    disposeLifecycle();
    disposeAgents();
    disposeEvents();
    agents.clear();
    epochs.clear();
    pending.clear();
  };
}
