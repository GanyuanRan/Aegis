const cache = new Map();

export function writeCache(key, value) {
  cache.set(key, { value, exportedAt: Date.now() });
}

export function readCache(key) {
  return cache.get(key)?.value;
}

export function exportCache() {
  return JSON.stringify([...cache.entries()]);
}

export function importCache(serialized) {
  cache.clear();
  for (const [key, entry] of JSON.parse(serialized)) {
    cache.set(key, entry);
  }
}
