/**
 * Thin DeepSeek Harness bundle adapter for Aegis Method Pack.
 *
 * The host-owned filesystem provider remains the discovery implementation.
 * This adapter points one isolated provider at this package's canonical
 * skills tree and contributes the compact router through native runtime context. It
 * does not copy skill bodies, replace the native skill tool, or add runtime
 * authority.
 */

import { fileURLToPath } from "node:url";
import { apply as applyFilesystemProvider } from "@deepseek-ai/dsh-skill-filesystem";
import { installBootstrap } from "./bootstrap.js";

const skillsRoot = fileURLToPath(new URL("../../skills/", import.meta.url));

export const name = "aegis-method-pack";
export const inject = ["skills", "agents", "systemPrompt"];

export function apply(ctx) {
  applyFilesystemProvider(ctx, {
    providerName: "aegis-method-pack",
    includeDefaultRoots: false,
    bundledSkillDir: skillsRoot,
    watch: false,
  });

  installBootstrap(ctx, { skillsRoot });
}
