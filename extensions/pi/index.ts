/**
 * Aegis extension for Pi CLI.
 *
 * Injects the compact using-aegis bootstrap before every LLM call (auto mode
 * only) and tracks a routing guard on the first non-readonly tool call —
 * mirroring the OpenCode plugin behavior through Pi's extension events.
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { createAegisHostAdapter } from "../shared/aegis-bootstrap.ts";

export default function (pi: ExtensionAPI) {
  createAegisHostAdapter(pi, {
    host: "pi",
    readonlyTools: ["read", "grep", "glob", "web_search", "websearch", "list"],
  });
}
