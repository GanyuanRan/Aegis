/**
 * Aegis extension for OMP (Oh My Pi, can1357/oh-my-pi).
 *
 * Same shared core as the Pi adapter, bound to OMP's extension events. OMP
 * additionally injects the using-aegis hot path natively through the
 * alwaysApply frontmatter; this extension provides the routing guard and a
 * belt-and-braces bootstrap when alwaysApply is not honored by the installed
 * OMP release.
 */

import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";
import { createAegisHostAdapter } from "../shared/aegis-bootstrap.ts";

export default function (pi: ExtensionAPI) {
  createAegisHostAdapter(pi, {
    host: "omp",
    readonlyTools: ["read", "grep", "glob", "web_search", "websearch", "ask", "list"],
  });
}
