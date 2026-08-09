/**
 * Aegis plugin for OpenCode.ai
 *
 * Injects compact Aegis bootstrap context via message transform.
 * Auto-registers skills directory via config hook (no symlinks needed).
 */

import path from 'path';
import fs from 'fs';
import os from 'os';
import { fileURLToPath } from 'url';
import { execFile } from 'node:child_process';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const MIRROR_MANIFEST_FILE = '.aegis-mirror-manifest.json';

// Simple frontmatter extraction (avoid dependency on skills-core for bootstrap)
const extractAndStripFrontmatter = (content) => {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);
  if (!match) return { frontmatter: {}, content };

  const frontmatterStr = match[1];
  const body = match[2].replace(/\r\n/g, '\n');
  const frontmatter = {};

  for (const line of frontmatterStr.split('\n')) {
    const colonIdx = line.indexOf(':');
    if (colonIdx > 0) {
      const key = line.slice(0, colonIdx).trim();
      const value = line.slice(colonIdx + 1).trim().replace(/^["']|["']$/g, '');
      frontmatter[key] = value;
    }
  }

  return { frontmatter, content: body };
};

// Normalize a path: trim whitespace, expand ~, resolve to absolute
const normalizePath = (p, homeDir) => {
  if (!p || typeof p !== 'string') return null;
  let normalized = p.trim();
  if (!normalized) return null;
  if (process.platform === 'win32') {
    const gitBashDrivePath = normalized.match(/^\/([a-zA-Z])(?:\/(.*))?$/);
    if (gitBashDrivePath) {
      const drive = `${gitBashDrivePath[1].toUpperCase()}:`;
      const rest = gitBashDrivePath[2] ? gitBashDrivePath[2].replace(/\//g, '\\') : '';
      normalized = rest ? `${drive}\\${rest}` : `${drive}\\`;
    }
  }
  if (normalized.startsWith('~/')) {
    normalized = path.join(homeDir, normalized.slice(2));
  } else if (normalized === '~') {
    normalized = homeDir;
  }
  return path.resolve(normalized);
};

const ensureDir = (dirPath) => {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
};

const symlinkType = process.platform === 'win32' ? 'junction' : 'dir';

const resolveHomeDir = () => {
  const fallback = os.homedir();
  return (
    normalizePath(process.env.HOME, fallback) ||
    normalizePath(process.env.USERPROFILE, fallback) ||
    fallback
  );
};

const readConfigValue = (homeDir, key) => {
  const configPath = path.join(homeDir, '.config/aegis/config.toml');
  if (!fs.existsSync(configPath)) return null;

  const content = fs.readFileSync(configPath, 'utf8');
  const lines = content.split(/\r?\n/);
  let configured = null;

  for (const line of lines) {
    const match = line.match(new RegExp(`^\\s*${key}\\s*=\\s*([^#]+)`));
    if (match) configured = match[1].trim().replace(/^["']|["']$/g, '');
  }

  return configured;
};

const readMirrorManifest = (targetDir) => {
  const manifestPath = path.join(targetDir, MIRROR_MANIFEST_FILE);
  if (!fs.existsSync(manifestPath)) return { skills: {} };

  try {
    const parsed = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    if (parsed && typeof parsed === 'object' && parsed.skills && typeof parsed.skills === 'object') {
      return parsed;
    }
  } catch {
    // Fall back to rebuilding the manifest from the current source tree.
  }

  return { skills: {} };
};

const writeMirrorManifest = (targetDir, manifest) => {
  ensureDir(targetDir);
  fs.writeFileSync(
    path.join(targetDir, MIRROR_MANIFEST_FILE),
    JSON.stringify({ ...manifest, updatedAt: new Date().toISOString() }, null, 2) + '\n',
    'utf8'
  );
};

const realpathOrNull = (targetPath) => {
  try {
    return fs.realpathSync(targetPath);
  } catch {
    return null;
  }
};

const readSkillMarkdown = (skillDir) => {
  const skillMarkdown = path.join(skillDir, 'SKILL.md');
  if (!fs.existsSync(skillMarkdown)) return null;
  return fs.readFileSync(skillMarkdown, 'utf8');
};

const detectMirrorMode = (skillTarget) => {
  try {
    return fs.lstatSync(skillTarget).isSymbolicLink() ? 'symlink' : 'copy';
  } catch {
    return 'unknown';
  }
};

const removeMirrorTarget = (skillTarget) => {
  fs.rmSync(skillTarget, { recursive: true, force: true });
};

const classifyExistingMirror = ({
  skillSource,
  bundledSkillSource,
  skillTarget,
  manifestEntry
}) => {
  if (!fs.existsSync(skillTarget)) return 'create';

  const sourceMarkdown = readSkillMarkdown(skillSource);
  if (!sourceMarkdown) return 'foreign';

  const sourceReal = realpathOrNull(skillSource);
  const bundledReal = bundledSkillSource ? realpathOrNull(bundledSkillSource) : null;
  const bundledMarkdown = bundledSkillSource ? readSkillMarkdown(bundledSkillSource) : null;
  const targetMarkdown = readSkillMarkdown(skillTarget);

  if (manifestEntry?.sourcePath) {
    if (manifestEntry.sourcePath === sourceReal && targetMarkdown === sourceMarkdown) {
      return 'current';
    }
    return 'refresh';
  }

  try {
    const stat = fs.lstatSync(skillTarget);
    if (stat.isSymbolicLink()) {
      const targetReal = realpathOrNull(skillTarget);
      if (targetReal === sourceReal) return 'claim-current';
      if (targetReal && bundledReal && targetReal === bundledReal) return 'refresh';
    }
  } catch {
    return 'foreign';
  }

  if (targetMarkdown === sourceMarkdown) return 'claim-current';
  if (bundledMarkdown && targetMarkdown === bundledMarkdown) {
    return bundledMarkdown === sourceMarkdown ? 'claim-current' : 'refresh';
  }

  return 'foreign';
};

const createMirrorTarget = (skillSource, skillTarget) => {
  try {
    fs.symlinkSync(skillSource, skillTarget, symlinkType);
    return 'symlink';
  } catch {
    // Fall back to a shallow recursive copy when symlinks are unavailable.
    fs.cpSync(skillSource, skillTarget, { recursive: true });
    return 'copy';
  }
};

const ensureSkillMirror = (sourceDir, targetDir, bundledSourceDir) => {
  if (!fs.existsSync(sourceDir)) return false;

  const entries = fs.readdirSync(sourceDir, { withFileTypes: true });
  const manifest = readMirrorManifest(targetDir);
  const nextManifest = { skills: {} };
  let mirrored = false;
  ensureDir(targetDir);

  for (const entry of entries) {
    if (!entry.isDirectory()) continue;

    const skillSource = path.join(sourceDir, entry.name);
    const bundledSkillSource = bundledSourceDir ? path.join(bundledSourceDir, entry.name) : null;
    const skillTarget = path.join(targetDir, entry.name);
    const skillMarkdown = path.join(skillSource, 'SKILL.md');

    if (!fs.existsSync(skillMarkdown)) continue;

    const classification = classifyExistingMirror({
      skillSource,
      bundledSkillSource,
      skillTarget,
      manifestEntry: manifest.skills?.[entry.name]
    });

    if (classification === 'foreign') continue;

    if (classification === 'refresh') {
      removeMirrorTarget(skillTarget);
    }

    let mirrorMode = detectMirrorMode(skillTarget);
    if (classification === 'create' || classification === 'refresh') {
      mirrorMode = createMirrorTarget(skillSource, skillTarget);
      mirrored = true;
    } else if (classification === 'claim-current') {
      mirrored = true;
    }

    nextManifest.skills[entry.name] = {
      sourcePath: realpathOrNull(skillSource),
      mirrorMode,
      managedAt: new Date().toISOString()
    };
  }

  for (const [skillName] of Object.entries(manifest.skills || {})) {
    if (nextManifest.skills[skillName]) continue;
    const staleTarget = path.join(targetDir, skillName);
    removeMirrorTarget(staleTarget);
    mirrored = true;
  }

  writeMirrorManifest(targetDir, nextManifest);
  return mirrored;
};

const readConfigActivationMode = (homeDir) => {
  const configured = readConfigValue(homeDir, 'activation_mode');
  return configured === 'explicit' || configured === 'auto' ? configured : 'auto';
};

const activationMode = (homeDir) => process.env.AEGIS_ACTIVATION_MODE || readConfigActivationMode(homeDir);

const readConfigTddMode = (homeDir) => {
  const configured = readConfigValue(homeDir, 'tdd_mode');
  return configured === 'off' || configured === 'auto' ? configured : 'off';
};

const tddMode = (homeDir) => {
  const configured = process.env.AEGIS_TDD_MODE || readConfigTddMode(homeDir);
  return configured === 'off' || configured === 'auto' ? configured : 'off';
};

const resolveConfiguredMethodPackRoot = (homeDir) => {
  const configuredRoot = normalizePath(
    process.env.AEGIS_METHOD_PACK_ROOT || readConfigValue(homeDir, 'method_pack_root'),
    homeDir
  );
  if (!configuredRoot) return null;

  const configuredSkillsDir = path.join(configuredRoot, 'skills');
  return fs.existsSync(configuredSkillsDir) ? configuredRoot : null;
};

const resolveSkillSource = (homeDir) => {
  const bundledMethodPackRoot = path.resolve(__dirname, '../..');
  const bundledSkillsDir = path.join(bundledMethodPackRoot, 'skills');
  const configuredMethodPackRoot = resolveConfiguredMethodPackRoot(homeDir);

  if (configuredMethodPackRoot) {
    return {
      methodPackRoot: configuredMethodPackRoot,
      skillsDir: path.join(configuredMethodPackRoot, 'skills'),
      bundledSkillsDir
    };
  }

  return {
    methodPackRoot: bundledMethodPackRoot,
    skillsDir: bundledSkillsDir,
    bundledSkillsDir
  };
};

const ROUTING_GUARD_MARKER = 'AEGIS_ROUTING_GUARD';

// Update self-check: OpenCode caches git plugins under
// ~/.cache/opencode/packages/<key>/node_modules/<pkg> via Bun and does not
// re-fetch on restart. To avoid stranding users on stale plugin versions, the
// plugin compares the remote HEAD against a recorded anchor on startup; when
// the remote moved, the cache entry is reset so the next launch re-installs.
const GIT_REMOTE = 'https://github.com/GanyuanRan/Aegis.git';
const UPDATE_STATE_FILE = '.aegis-plugin-state.json';
const UPDATE_REMINDER_TEXT =
  '**Aegis update:** a newer Aegis release was detected and the OpenCode plugin cache was reset. Restart OpenCode to load the updated plugin.';

export const resolveCacheInstall = (pluginDir) => {
  // Bun caches git plugins as nested directories under
  // ~/.cache/opencode/packages/<git-url-parts...>/node_modules/aegis
  const packageRoot = path.resolve(pluginDir, '..', '..');
  const nodeModulesDir = path.dirname(packageRoot);
  if (path.basename(nodeModulesDir) !== 'node_modules') return null;

  let name = '';
  try {
    name = JSON.parse(fs.readFileSync(path.join(packageRoot, 'package.json'), 'utf8')).name || '';
  } catch {
    return null;
  }
  if (name !== 'aegis') return null;

  // The cache entry to reset is the git package directory holding node_modules.
  const cacheKeyDir = path.dirname(nodeModulesDir);

  // Walk up to confirm the cache-key directory lives under
  // <something>/.cache/opencode/packages/... so we never delete a local checkout.
  let cursor = cacheKeyDir;
  for (let i = 0; i < 12; i += 1) {
    const parent = path.dirname(cursor);
    if (path.basename(cursor) === 'packages') {
      const opencodeCacheDir = parent;
      const cacheRoot = path.dirname(opencodeCacheDir);
      const isBunCache =
        path.basename(opencodeCacheDir) === 'opencode' && path.basename(cacheRoot) === '.cache';
      return isBunCache ? { packageRoot, cacheKeyDir } : null;
    }
    cursor = parent;
  }
  return null;
};

export const readUpdateState = (configDir) => {
  try {
    return JSON.parse(fs.readFileSync(path.join(configDir, UPDATE_STATE_FILE), 'utf8')) || {};
  } catch {
    return {};
  }
};

const writeUpdateState = (configDir, state) => {
  try {
    fs.writeFileSync(path.join(configDir, UPDATE_STATE_FILE), JSON.stringify(state, null, 2) + '\n', 'utf8');
  } catch {
    // State bookkeeping must never break startup.
  }
};

const readCachedVersion = (packageRoot) => {
  try {
    return JSON.parse(fs.readFileSync(path.join(packageRoot, 'package.json'), 'utf8')).version || 'unknown';
  } catch {
    return 'unknown';
  }
};

const defaultExecGitHead = async (remote, timeoutMs = 3000) => {
  return new Promise((resolve) => {
    execFile('git', ['ls-remote', remote, 'HEAD'], { timeout: timeoutMs }, (err, stdout) => {
      if (err) return resolve(null);
      const head = stdout.trim().split(/\s+/)[0];
      resolve(head || null);
    });
  });
};

// Startup self-check. Never blocks startup: any failure is a silent skip.
// Exported so tests can inject a fake execGitHead and a fake plugin location.
export const performUpdateCheck = async ({
  pluginDir,
  configDir,
  execGitHead = defaultExecGitHead,
  now = () => new Date(),
  logger = console
}) => {
  const cache = resolveCacheInstall(pluginDir);
  if (!cache) return { status: 'not-cache-install' };

  const state = readUpdateState(configDir);
  const version = readCachedVersion(cache.packageRoot);
  const nextState = { ...state, installedVersion: version, lastCheckedAt: now().toISOString() };

  let remoteHead = null;
  try {
    remoteHead = await execGitHead(GIT_REMOTE);
  } catch {
    remoteHead = null;
  }

  if (!remoteHead) {
    writeUpdateState(configDir, nextState);
    return { status: 'check-failed', version };
  }

  nextState.lastRemoteHead = remoteHead;

  if (!state.lastRemoteHead) {
    // First check on this cache: record the anchor, do not delete anything.
    writeUpdateState(configDir, nextState);
    return { status: 'anchored', version, remoteHead };
  }

  if (state.lastRemoteHead === remoteHead) {
    writeUpdateState(configDir, nextState);
    return { status: 'current', version, remoteHead };
  }

  // Remote moved: reset the Bun cache entry so the next launch installs the
  // latest release. The running plugin keeps working until then.
  try {
    fs.rmSync(cache.cacheKeyDir, { recursive: true, force: true });
    nextState.updatePending = true;
    writeUpdateState(configDir, nextState);
    return { status: 'cache-reset', version, remoteHead };
  } catch (err) {
    logger.error('[aegis] update self-check could not reset the plugin cache:', err.message);
    return { status: 'reset-failed', version, remoteHead };
  }
};

// After a cache reset, the next launch runs the freshly installed plugin. Clear
// the pending reminder once the cached version actually changed.
export const reconcilePendingUpdate = (configDir, packageRoot) => {
  try {
    const state = readUpdateState(configDir);
    if (!state.updatePending) return;
    const currentVersion = readCachedVersion(packageRoot);
    if (state.installedVersion && currentVersion !== 'unknown' && state.installedVersion !== currentVersion) {
      const { updatePending, ...rest } = state;
      writeUpdateState(configDir, rest);
    }
  } catch {
    // Bookkeeping only; never break startup.
  }
};

const pendingUpdateReminder = (configDir) =>
  readUpdateState(configDir).updatePending ? `\n\n${UPDATE_REMINDER_TEXT}` : '';

const READONLY_TOOLS = new Set([
  'read',
  'glob',
  'grep',
  'webfetch',
  'websearch',
  'context7_resolve-library-id',
  'context7_get-library-docs',
  'sequential-thinking_sequentialthinking'
]);

const getSessionState = (state, sessionID) => {
  if (state.size > 500) state.clear();
  let entry = state.get(sessionID);
  if (!entry) {
    entry = { sawSkillCall: false, guardFired: false };
    state.set(sessionID, entry);
  }
  return entry;
};

const buildRoutingGuardText = () => `\n[${ROUTING_GUARD_MARKER}] No routing decision was recorded before this session's first non-readonly tool call. If this task is non-trivial, call the \`skill\` tool now and load the matching Aegis skill (for example brainstorming, systematic-debugging, writing-plans, or verification-before-completion); otherwise explicitly declare \`Route: fast-path\` with a reason. Advisory only; execution continues.\n`;

export const AegisPlugin = async ({ client, directory }) => {
  const homeDir = resolveHomeDir();
  const { methodPackRoot, skillsDir: aegisSkillsDir, bundledSkillsDir } = resolveSkillSource(homeDir);
  const envConfigDir = normalizePath(process.env.OPENCODE_CONFIG_DIR, homeDir);
  const configDir = envConfigDir || path.join(homeDir, '.config/opencode');
  const globalSkillsDir = path.join(configDir, 'skills');

  const sessionState = new Map();

  // Keep Aegis skills inside an OpenCode-native discovery path.
  // The host currently documents ~/.config/opencode/skills as a supported
  // global location, while config hook discovery is an implementation detail.
  // When a user-local method_pack_root is configured, treat it as the canonical
  // Aegis body and generate this OpenCode view from that source instead of from
  // a second host-local checkout.
  ensureSkillMirror(aegisSkillsDir, globalSkillsDir, bundledSkillsDir);

  // Update self-check (fire-and-forget, never blocks startup): when the plugin
  // runs from OpenCode's Bun cache and the remote HEAD moved, reset the cache
  // entry so the next launch re-installs the latest release.
  reconcilePendingUpdate(configDir, path.resolve(__dirname, '..', '..'));
  performUpdateCheck({ pluginDir: __dirname, configDir })
    .then((result) => {
      if (result.status === 'cache-reset') {
        console.log(`[aegis] update self-check: reset stale plugin cache (cached ${result.version}); restart OpenCode to load the latest release`);
      } else if (result.status === 'not-cache-install') {
        // Development checkout or test environment; nothing to refresh.
      }
    })
    .catch(() => {
      // The self-check must never interfere with plugin startup.
    });

  // Helper to generate compact bootstrap content
  const getBootstrapContent = () => {
    // Try to load using-aegis skill
    const skillPath = path.join(aegisSkillsDir, 'using-aegis', 'SKILL.md');
    if (!fs.existsSync(skillPath)) return null;

    const fullContent = fs.readFileSync(skillPath, 'utf8');
    const { content } = extractAndStripFrontmatter(fullContent);

    const toolMapping = `**Tool Mapping for OpenCode:**
When skills reference tools you don't have, substitute OpenCode equivalents:
- \`TodoWrite\` → \`todowrite\`
- \`Task\` tool with subagents → Use OpenCode's subagent system (@mention)
- \`Skill\` tool → OpenCode's native \`skill\` tool
- \`Read\`, \`Write\`, \`Edit\`, \`Bash\` → Your native tools

Use OpenCode's native \`skill\` tool to list and load skills.`;

    return `<EXTREMELY_IMPORTANT>
You have Aegis.
${pendingUpdateReminder(configDir)}

Aegis TDD mode: ${tddMode(homeDir)}. off is the default and disables automatic TDD while verification-before-completion still applies; auto routes strict TDD only when risk warrants.

**ROUTING CONTRACT (this turn):** Before your first non-readonly tool call you MUST either (1) call the \`skill\` tool and load the relevant Aegis skill for this task, or (2) explicitly declare \`Route: fast-path\` with a one-line reason. There is no silent pass: doing neither triggers a visible routing-guard marker on your first non-readonly tool call. The compact using-aegis hot path is already loaded below, so do not load it again; load the task-specific skill a rule below matches, or declare fast-path.

${content}

${toolMapping}
</EXTREMELY_IMPORTANT>`;
  };

  return {
    // Inject skills path into live config so OpenCode discovers Aegis skills
    // without requiring manual symlinks or config file edits.
    // This works because Config.get() returns a cached singleton — modifications
    // here are visible when skills are lazily discovered later.
    config: async (config) => {
      config.skills = config.skills || {};
      config.skills.paths = config.skills.paths || [];
      if (!config.skills.paths.includes(globalSkillsDir)) {
        config.skills.paths.push(globalSkillsDir);
      }
    },

    // Inject bootstrap into the first user message of each session.
    // Using a user message instead of a system message avoids:
    //   1. Token bloat from system messages repeated every turn (#750)
    //   2. Multiple system messages breaking Qwen and other models (#894)
    'experimental.chat.messages.transform': async (_input, output) => {
      if (activationMode(homeDir) === 'explicit') return;
      const bootstrap = getBootstrapContent();
      if (!bootstrap || !output.messages.length) return;
      const firstUser = output.messages.find(m => m.info.role === 'user');
      if (!firstUser || !firstUser.parts.length) return;
      // Only inject once
      if (firstUser.parts.some(p => p.type === 'text' && p.text.includes('EXTREMELY_IMPORTANT'))) return;
      const ref = firstUser.parts[0];
      firstUser.parts.unshift({ ...ref, type: 'text', text: bootstrap });
    },

    // Record skill loading so the routing guard can see it.
    'tool.execute.before': async ({ tool, sessionID }) => {
      if (tool === 'skill') getSessionState(sessionState, sessionID).sawSkillCall = true;
    },

    // Routing guard: in auto mode, visibly flag the first non-readonly tool
    // call that happens without a recorded skill load. Advisory only; never
    // blocks execution. explicit mode disables it together with bootstrap
    // injection.
    'tool.execute.after': async ({ tool, sessionID }, output) => {
      if (activationMode(homeDir) !== 'auto') return;
      const state = getSessionState(sessionState, sessionID);
      if (tool === 'skill') {
        state.sawSkillCall = true;
        return;
      }
      if (state.sawSkillCall || state.guardFired) return;
      if (READONLY_TOOLS.has(tool)) return;
      state.guardFired = true;
      output.output = `${buildRoutingGuardText()}${output.output ?? ''}`;
    }
  };
};
