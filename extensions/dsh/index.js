/**
 * Thin DeepSeek Harness bundle adapter for Aegis Method Pack.
 *
 * The host-owned filesystem provider remains the discovery implementation.
 * This adapter only points one isolated provider at this package's canonical
 * skills tree; it does not copy skill bodies or add runtime authority.
 */

import { fileURLToPath } from "node:url";
import { apply as applyFilesystemProvider } from "@deepseek-ai/dsh-skill-filesystem";

const skillsRoot = fileURLToPath(new URL("../../skills/", import.meta.url));

export const name = "aegis-method-pack";
export const inject = ["skills"];

export function apply(ctx) {
  applyFilesystemProvider(ctx, {
    providerName: "aegis-method-pack",
    includeDefaultRoots: false,
    bundledSkillDir: skillsRoot,
    watch: false,
  });
}
