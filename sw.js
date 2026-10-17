// Keeps the ledger opening when the local server isn't running. Network first, so a
// git pull shows up on the next launch; the cached copy is only used when offline.
const CACHE = "dnd-ledger-v2";
const SHELL = ["./", "index.html", "manifest.webmanifest", "data/example-character.json", "data/character-template.json", "data/srd-spells.json", "data/srd-items.json", "data/base-pack.json", "data/content-pack-example.json", "assets/icons/icon-192.png", "assets/icons/icon-512.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", e => {
  const u = new URL(e.request.url);
  if (e.request.method !== "GET" || u.origin !== location.origin || u.pathname.startsWith("/api/")) return;
  e.respondWith(fetch(e.request).then(r => { if (r.ok) { const c = r.clone(); caches.open(CACHE).then(x => x.put(e.request, c)); } return r; })
    .catch(() => caches.match(e.request).then(r => r || caches.match("index.html"))));
});
