/**
 * Aegis shared extension core for Pi / OMP coding agents.
 *
 * Pure logic with no host-specific API dependency: config resolution, compact
 * bootstrap generation, and routing-guard bookkeeping. Host adapters (pi/omp)
 * bind these helpers to their extension events.
 *
 * The compact bootstrap mirrors what the OpenCode plugin injects, so routing
 * discipline is consistent across hosts.
 */

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

export interface AegisConfig {
  activationMode: "auto" | "explicit";
  tddMode: "auto" | "off";
}

export interface GuardState {
  sawSkillLoad: boolean;
  guardFired: boolean;
  firstNonReadonly: boolean;
}

export const ROUTING_GUARD_MARKER = "AEGIS_ROUTING_GUARD";
export const BOOTSTRAP_MARKER = "EXTREMELY_IMPORTANT";

const FRONTMATTER_RE = /^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/;

export function resolveHomeDir(): string {
  const fallback = os.homedir();
  return process.env.HOME || process.env.USERPROFILE || fallback;
}

export function resolveMethodPackRoot(entryDir: string): string | null {
  const configRoot = readConfigValue(resolveHomeDir(), "method_pack_root");
  const envRoot = process.env.AEGIS_METHOD_PACK_ROOT || configRoot;
  if (envRoot) {
    const expanded = envRoot.replace(/^~[\\/]/, `${resolveHomeDir()}/`);
    const resolved = path.resolve(expanded);
    if (fs.existsSync(path.join(resolved, "skills", "using-aegis", "SKILL.md"))) {
      return resolved;
    }
  }
  // Fall back to the nearest ancestor holding the using-aegis skill: works for
  // the bundled checkout (<root>/extensions/<host>), for a shared/ submodule
  // (<root>/extensions/shared), and for nested copy installs.
  let cursor = entryDir;
  for (let i = 0; i < 8; i += 1) {
    if (fs.existsSync(path.join(cursor, "skills", "using-aegis", "SKILL.md"))) {
      return cursor;
    }
    const parent = path.dirname(cursor);
    if (parent === cursor) break;
    cursor = parent;
  }
  return null;
}

export function readConfigValue(homeDir: string, key: string): string | null {
  try {
    const configPath = path.join(homeDir, ".config", "aegis", "config.toml");
    if (!fs.existsSync(configPath)) return null;
    const lines = fs.readFileSync(configPath, "utf8").split(/\r?\n/);
    let value: string | null = null;
    for (const line of lines) {
      const match = line.match(new RegExp(`^\\s*${key}\\s*=\\s*([^#]+)`));
      if (match) value = match[1].trim().replace(/^["']|["']$/g, "");
    }
    return value;
  } catch {
    return null;
  }
}

export function readConfig(homeDir: string): AegisConfig {
  const envMode = process.env.AEGIS_ACTIVATION_MODE;
  const configMode = readConfigValue(homeDir, "activation_mode");
  const activationMode =
    envMode === "explicit" || envMode === "auto"
      ? envMode
      : configMode === "explicit" || configMode === "auto"
        ? configMode
        : "auto";

  const envTdd = process.env.AEGIS_TDD_MODE;
  const configTdd = readConfigValue(homeDir, "tdd_mode");
  const tddMode =
    envTdd === "auto" || envTdd === "off"
      ? envTdd
      : configTdd === "auto" || configTdd === "off"
        ? configTdd
        : "off";

  return { activationMode, tddMode };
}

export function stripFrontmatter(content: string): string {
  const match = content.match(FRONTMATTER_RE);
  return (match ? match[2] : content).replace(/\r\n/g, "\n");
}

export function readUsingAegisBody(methodPackRoot: string): string | null {
  try {
    const skillPath = path.join(methodPackRoot, "skills", "using-aegis", "SKILL.md");
    if (!fs.existsSync(skillPath)) return null;
    return stripFrontmatter(fs.readFileSync(skillPath, "utf8"));
  } catch {
    return null;
  }
}

export function buildBootstrap(
  body: string,
  opts: {
    tddMode: "auto" | "off";
    host: string;
    toolMapping: string;
  }
): string {
  const { tddMode, host, toolMapping } = opts;
  return `<${BOOTSTRAP_MARKER}>
You have Aegis.

Aegis TDD mode: ${tddMode}. off is the default and disables automatic TDD while verification-before-completion still applies; auto routes strict TDD only when risk warrants.

**ROUTING CONTRACT (this turn):** Before your first non-readonly tool call you MUST either (1) load the relevant Aegis skill for this task (by reading its SKILL.md or skill:// entry as ${host} discovers it), or (2) explicitly declare \`Route: fast-path\` with a one-line reason. There is no silent pass: doing neither triggers a visible routing-guard marker on your first non-readonly tool call. The compact using-aegis hot path is already loaded below, so do not load it again; load the task-specific skill a rule below matches, or declare fast-path.

${body}

${toolMapping}
</${BOOTSTRAP_MARKER}>`;
}

export function defaultToolMapping(host: string): string {
  if (host === "pi") {
    return `**Tool Mapping for Pi:**
When skills reference tools you don't have, substitute Pi equivalents:
- \`TodoWrite\` → Pi's todo tracking or \`pi\` extension conventions
- \`Task\` tool with subagents → Pi's subagent/task flows
- \`Skill\` tool → read the SKILL.md file Pi discovered (skills are progressive-disclosure files; load the relevant one on demand)
- \`Read\`, \`Write\`, \`Edit\`, \`Bash\` → Pi's native \`read\`, \`write\`, \`edit\`, \`bash\` tools`;
  }
  return `**Tool Mapping for OMP:**
When skills reference tools you don't have, substitute OMP equivalents:
- \`TodoWrite\` → OMP's \`todo\` tool
- \`Task\` tool with subagents → OMP's \`task\` tool
- \`Skill\` tool → \`read skill://<name>\` for the skill content OMP discovered
- \`Read\`, \`Write\`, \`Edit\`, \`Bash\` → OMP's native \`read\`, \`write\`, \`edit\`, \`bash\` tools`;
}

export function buildRoutingGuardText(): string {
  return `\n[${ROUTING_GUARD_MARKER}] No routing decision was recorded before this session's first non-readonly tool call. If this task is non-trivial, load the matching Aegis skill now (for example brainstorming, systematic-debugging, writing-plans, or verification-before-completion); otherwise explicitly declare \`Route: fast-path\` with a reason. Advisory only; execution continues.\n`;
}

export function createGuardState(): GuardState {
  return { sawSkillLoad: false, guardFired: false, firstNonReadonly: false };
}

/**
 * Decide whether a tool call counts as a skill load for routing purposes.
 * Pi/OMP load skills by reading their SKILL.md files; OMP also exposes
 * skill:// URLs through the read tool.
 */
export function isSkillLoad(toolName: string, inputArgs: Record<string, unknown>): boolean {
  if (toolName === "skill") return true;
  if (toolName !== "read") return false;
  const argValues: string[] = [];
  for (const value of Object.values(inputArgs || {})) {
    if (typeof value === "string") argValues.push(value);
  }
  return argValues.some((v) => v.includes("SKILL.md") || v.includes("skill://"));
}

export function isReadonlyTool(toolName: string, readonlyTools: string[]): boolean {
  return readonlyTools.includes(toolName);
}

export interface GuardDecision {
  mark: boolean;
  state: GuardState;
}

/**
 * Routing guard: track whether the session loaded a skill before its first
 * non-readonly tool call. Returns mark=true once, when the guard fires.
 */
export function updateGuard(
  state: GuardState,
  toolName: string,
  inputArgs: Record<string, unknown>,
  readonlyTools: string[]
): GuardDecision {
  if (isSkillLoad(toolName, inputArgs)) {
    state.sawSkillLoad = true;
    return { mark: false, state };
  }
  if (state.sawSkillLoad || state.guardFired) {
    return { mark: false, state };
  }
  if (isReadonlyTool(toolName, readonlyTools)) {
    return { mark: false, state };
  }
  state.firstNonReadonly = true;
  state.guardFired = true;
  return { mark: true, state };
}

/**
 * Shared host-adapter logic for Pi / OMP extensions: injects the compact
 * bootstrap into every LLM call (auto mode only) and appends the routing-guard
 * marker to the first non-readonly tool result without a recorded decision.
 *
 * The injected `pi` object only needs: on(event, handler) with handlers
 * receiving { messages } / { toolName, input, toolCallId } / { toolCallId,
 * content } plus a ctx carrying sessionManager.getSessionId().
 */
export function createAegisHostAdapter(
  pi: {
    on: (event: string, handler: (event: any, ctx?: any) => any) => void;
  },
  opts: { host: string; readonlyTools: string[] }
): void {
  const { host, readonlyTools } = opts;
  const homeDir = resolveHomeDir();
  const entryDir = path.dirname(fileURLToPath(import.meta.url));
  const methodPackRoot = resolveMethodPackRoot(entryDir);
  const bootstrapBody = methodPackRoot ? readUsingAegisBody(methodPackRoot) : null;
  const config = readConfig(homeDir);

  const guardStates = new Map<string, GuardState>();
  const pendingMarks = new Map<string, boolean>();

  const getGuardState = (sessionId: string): GuardState => {
    if (guardStates.size > 500) guardStates.clear();
    let state = guardStates.get(sessionId);
    if (!state) {
      state = createGuardState();
      guardStates.set(sessionId, state);
    }
    return state;
  };

  const bootstrapText = bootstrapBody
    ? buildBootstrap(bootstrapBody, { tddMode: config.tddMode, host, toolMapping: defaultToolMapping(host) })
    : null;

  // Inject the compact hot path into every LLM call in auto mode. Using the
  // context event keeps it session-free and deduplicated, like the OpenCode
  // plugin's first-message transform without per-session persistence.
  pi.on("context", async (event: any) => {
    if (config.activationMode !== "auto" || !bootstrapText) return;
    const messages = event.messages || [];
    const firstUser = messages.find((m: any) => m.role === "user");
    if (!firstUser) return;
    const serialized = JSON.stringify(firstUser.content ?? "");
    if (serialized.includes(BOOTSTRAP_MARKER)) return;
    const part = { type: "text", text: bootstrapText };
    if (Array.isArray(firstUser.content)) {
      firstUser.content.unshift(part);
    } else if (typeof firstUser.content === "string") {
      firstUser.content = [{ ...part }, { type: "text", text: firstUser.content }];
    } else {
      firstUser.content = [part];
    }
    return { messages };
  });

  // Record skill loads and flag the first non-readonly call without a routing
  // decision. Advisory only; never blocks.
  pi.on("tool_call", async (event: any, ctx: any) => {
    const sessionId = ctx?.sessionManager?.getSessionId?.() ?? "default";
    const state = getGuardState(sessionId);
    const decision = updateGuard(state, event.toolName, event.input ?? {}, readonlyTools);
    if (decision.mark) {
      pendingMarks.set(event.toolCallId, true);
    }
  });

  pi.on("tool_result", async (event: any) => {
    if (!pendingMarks.get(event.toolCallId)) return;
    pendingMarks.delete(event.toolCallId);
    const content = Array.isArray(event.content) ? event.content : [];
    return {
      content: [{ type: "text", text: buildRoutingGuardText() }, ...content],
    };
  });
}
