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

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Simple frontmatter extraction (avoid dependency on skills-core for bootstrap)
const extractAndStripFrontmatter = (content) => {
  const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) return { frontmatter: {}, content };

  const frontmatterStr = match[1];
  const body = match[2];
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

const ensureSkillMirror = (sourceDir, targetDir) => {
  if (!fs.existsSync(sourceDir)) return false;

  const entries = fs.readdirSync(sourceDir, { withFileTypes: true });
  let mirrored = false;
  ensureDir(targetDir);

  for (const entry of entries) {
    if (!entry.isDirectory()) continue;

    const skillSource = path.join(sourceDir, entry.name);
    const skillTarget = path.join(targetDir, entry.name);
    const skillMarkdown = path.join(skillSource, 'SKILL.md');

    if (!fs.existsSync(skillMarkdown) || fs.existsSync(skillTarget)) continue;

    try {
      fs.symlinkSync(skillSource, skillTarget, symlinkType);
      mirrored = true;
    } catch {
      // Fall back to a shallow recursive copy when symlinks are unavailable.
      fs.cpSync(skillSource, skillTarget, { recursive: true });
      mirrored = true;
    }
  }

  return mirrored;
};

const readConfigActivationMode = (homeDir) => {
  const configPath = path.join(homeDir, '.config/aegis/config.toml');
  if (!fs.existsSync(configPath)) return 'auto';

  const content = fs.readFileSync(configPath, 'utf8');
  const lines = content.split(/\r?\n/);
  let configured = null;

  for (const line of lines) {
    const match = line.match(/^\s*activation_mode\s*=\s*([^#]+)/);
    if (match) configured = match[1].trim().replace(/^["']|["']$/g, '');
  }

  return configured === 'explicit' || configured === 'auto' ? configured : 'auto';
};

const activationMode = (homeDir) => process.env.AEGIS_ACTIVATION_MODE || readConfigActivationMode(homeDir);

export const AegisPlugin = async ({ client, directory }) => {
  const homeDir = os.homedir();
  const aegisSkillsDir = path.resolve(__dirname, '../../skills');
  const envConfigDir = normalizePath(process.env.OPENCODE_CONFIG_DIR, homeDir);
  const configDir = envConfigDir || path.join(homeDir, '.config/opencode');
  const globalSkillsDir = path.join(configDir, 'skills');

  // Keep Aegis skills inside an OpenCode-native discovery path.
  // The host currently documents ~/.config/opencode/skills as a supported
  // global location, while config hook discovery is an implementation detail.
  ensureSkillMirror(aegisSkillsDir, globalSkillsDir);

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

**IMPORTANT: The compact using-aegis hot path is included below. For task-specific workflows, use OpenCode's native \`skill\` tool to load only the relevant skill or reference.**

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
    }
  };
};
