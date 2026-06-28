import assert from "node:assert/strict";
import { renderThemeLabel } from "./settings.js";

assert.equal(renderThemeLabel({ theme: "" }), "system");
assert.equal(renderThemeLabel({ theme: "dark" }), "dark");
