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
      kind: "plugin",
      plugin: "aegis",
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

  return ctx.on("agent/session-start", ({ agent }) => {
    if (agent.session?.header?.origin === "subagent") return;
    agent.inject(createBootstrapMessage(createUserMessage, bootstrap));
  });
}
