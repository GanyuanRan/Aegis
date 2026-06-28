import assert from "node:assert/strict";
import { exportCache, importCache, readCache, writeCache } from "./cache.js";

writeCache("theme", "system");
const snapshot = exportCache();
importCache(snapshot);

assert.equal(readCache("theme"), "system");
