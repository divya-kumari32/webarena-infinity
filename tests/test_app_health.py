import textwrap
from pathlib import Path

import pytest

from infra import app_health

# Minimal correct server.py (mirrors the real reference server contract).
GOOD_SERVER = textwrap.dedent('''
    import http.server, json, socketserver, sys, threading
    _state=None; _seed=None; _lock=threading.Lock()
    class H(http.server.SimpleHTTPRequestHandler):
        def do_PUT(self):
            global _state,_seed
            if self.path=="/api/state":
                n=int(self.headers.get("Content-Length",0)); b=self.rfile.read(n)
                with _lock:
                    _state=json.loads(b)
                    if _seed is None: _seed=json.loads(json.dumps(_state))
                self.send_response(200); self.end_headers(); self.wfile.write(b\'{"status":"ok"}\')
            else: self.send_error(404)
        def do_POST(self):
            global _state
            if self.path=="/api/reset":
                with _lock: _state=json.loads(json.dumps(_seed)) if _seed else None
                self.send_response(200); self.end_headers(); self.wfile.write(b\'{"status":"ok"}\')
            else: self.send_error(404)
        def do_GET(self):
            if self.path=="/api/state":
                with _lock: s=_state
                if s is None: self.send_response(404); self.end_headers(); self.wfile.write(b\'{}\')
                else: self.send_response(200); self.end_headers(); self.wfile.write(json.dumps(s).encode())
            else: super().do_GET()
        def log_message(self,*a): pass
    class T(socketserver.ThreadingMixIn, http.server.HTTPServer): daemon_threads=True
    port=int(sys.argv[sys.argv.index("--port")+1]) if "--port" in sys.argv else 8000
    T(("",port),H).serve_forever()
''')

# index.html whose JS PUTs state on load (passes the browser-load check).
GOOD_INDEX = textwrap.dedent('''
    <!doctype html><html><body><div id=app>ok</div>
    <script>
      fetch('/api/state',{method:'PUT',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({loaded:true})});
    </script></body></html>
''')

# index.html whose JS throws before PUTting (fails the browser-load check).
BROKEN_JS_INDEX = textwrap.dedent('''
    <!doctype html><html><body><div id=app>x</div>
    <script> nonexistentFunction();
      fetch('/api/state',{method:'PUT',body:'{}'}); </script></body></html>
''')


def _make_app(d: Path, server: str, index: str):
    (d / "server.py").write_text(server)
    (d / "index.html").write_text(index)
    (d / "js").mkdir(exist_ok=True); (d / "js" / "app.js").write_text("// noop")
    (d / "css").mkdir(exist_ok=True); (d / "css" / "styles.css").write_text("body{}")


def test_good_app_passes(tmp_path, free_port):
    _make_app(tmp_path, GOOD_SERVER, GOOD_INDEX)
    ok, diag = app_health.run_health_gate(tmp_path, port=free_port)
    assert ok, diag


def test_missing_files_fails_structural(tmp_path, free_port):
    (tmp_path / "server.py").write_text(GOOD_SERVER)  # no index.html / js / css
    ok, diag = app_health.run_health_gate(tmp_path, port=free_port)
    assert not ok
    assert "index.html" in diag or "missing" in diag.lower()


def test_server_that_crashes_on_boot_fails(tmp_path, free_port):
    _make_app(tmp_path, "import sys; sys.exit(1)\n", GOOD_INDEX)
    ok, diag = app_health.run_health_gate(tmp_path, port=free_port)
    assert not ok
    assert "boot" in diag.lower() or "did not start" in diag.lower()


def test_app_whose_js_never_pushes_state_fails_browser_check(tmp_path, free_port):
    _make_app(tmp_path, GOOD_SERVER, BROKEN_JS_INDEX)
    ok, diag = app_health.run_health_gate(tmp_path, port=free_port)
    assert not ok
    assert "state" in diag.lower()  # "app JS did not PUT state ..."
