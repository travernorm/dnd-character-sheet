#!/usr/bin/env python3
"""Run the D&D Ledger on this computer.

Serves the repo folder at http://localhost:8790 and adds one endpoint the page uses
when a session is closed: POST /api/backup writes backups/<date>-session-<n>.json,
commits it and pushes to GitHub with this computer's git login.

GET /api/packs lists the .json files in packs/ (content packs from your own books).

Usage: python3 tools/serve.py [--port 8790]
"""
import http.server, json, os, re, subprocess, sys, functools

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_RE = re.compile(r"^backups/[A-Za-z0-9._-]+\.json$")


def git(*args, timeout=60):
    r = subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stdout + r.stderr).strip()


def repo_web_url():
    code, url = git("remote", "get-url", "origin")
    if code:
        return None
    m = re.search(r"github\.com[:/](.+?)(?:\.git)?$", url)
    return "https://github.com/" + m.group(1) if m else None


def backup(body):
    rel = body.get("file", "")
    if not FILE_RE.match(rel):
        return 400, {"ok": False, "error": "bad file name"}
    data = body.get("data")
    if not isinstance(data, dict) or data.get("format") not in ("yoruba-ledger", "dnd-ledger"):
        return 400, {"ok": False, "error": "not a ledger backup"}
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write("\n")
    msg = str(body.get("message") or "Ledger backup")[:200]
    git("add", "--", rel)
    code, out = git("commit", "-m", msg, "--", rel)
    if code and "nothing to commit" not in out:
        return 200, {"ok": True, "written": rel, "pushed": False, "error": "commit failed: " + out[-300:]}
    _, sha = git("rev-parse", "HEAD")
    code, out = git("push", "origin", "HEAD", timeout=120)
    if code:  # behind GitHub: bring it in, then try once more
        git("pull", "--rebase", "--autostash", "origin", "HEAD", timeout=120)
        _, sha = git("rev-parse", "HEAD")
        code, out = git("push", "origin", "HEAD", timeout=120)
    web = repo_web_url()
    res = {"ok": True, "written": rel, "commit": sha, "pushed": code == 0}
    if web:
        res["commitUrl"] = web + "/commit/" + sha
    if code:
        res["error"] = out[-300:]
    return 200, res


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def _json(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path.startswith("/api/ping"):
            return self._json(200, {"ok": True, "app": "dnd-ledger"})
        if self.path.startswith("/api/packs"):  # content packs in the git-ignored packs/ folder
            d = os.path.join(ROOT, "packs")
            files = sorted(f for f in os.listdir(d) if f.endswith(".json")) if os.path.isdir(d) else []
            return self._json(200, {"ok": True, "files": files})
        return super().do_GET()

    def do_POST(self):
        if self.path != "/api/backup":
            return self._json(404, {"ok": False})
        if self.headers.get("Origin") not in (None, "http://localhost:%d" % PORT, "http://127.0.0.1:%d" % PORT):
            return self._json(403, {"ok": False, "error": "wrong origin"})
        try:
            n = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(n) or b"{}")
            code, res = backup(body)
        except Exception as e:  # report, don't crash the server
            code, res = 500, {"ok": False, "error": str(e)}
        return self._json(code, res)

    def log_message(self, fmt, *args):
        if "/api/" in (args[0] if args else ""):
            super().log_message(fmt, *args)


if __name__ == "__main__":
    PORT = 8790
    if "--port" in sys.argv:
        PORT = int(sys.argv[sys.argv.index("--port") + 1])
    handler = functools.partial(Handler, directory=ROOT)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler)
    print("D&D Ledger on http://localhost:%d" % PORT, flush=True)
    srv.serve_forever()
