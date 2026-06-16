# Pipeline Self-Healing Hardening — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `infra/pipeline.py` run hands-off — every known failure mode is detected and handled automatically (retry / backoff / model-driven regenerate / clean classified exit), with a live activity log so the user always knows what's happening.

**Architecture:** Add focused, independently-testable helper modules (`recovery`, `app_health`, `status`, `cleanup_results`) and wire them into `pipeline.py` via two thin "guarded phase" wrappers (Approach C — no `main()` rewrite). The pipeline only *validates and orchestrates*; the **model authors all app/task code**. Every exit is classified; nothing crashes ambiguously or hangs silently.

**Tech Stack:** Python ≥3.12, `uv`, `pytest`, `requests`, Playwright **sync** API (already installed for eval), `browser_use` (eval), standard library.

**Spec:** `docs/superpowers/specs/2026-06-16-pipeline-self-healing-hardening-design.md`

**Branch:** all work on `pipeline-hardening` (already created off `app_gen_v1`).

---

## Conventions for every task

- Run tests with the project venv: `.venv/bin/pytest`.
- Commit messages: no `Co-Authored-By` line (project rule).
- Never commit `*.bsub` (gitignored).
- Keep each new module focused and small.

---

### Task 0: Test scaffolding

**Files:**
- Modify: `pyproject.toml` (add dev deps)
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Add pytest dev dependencies**

Run:
```bash
uv add --dev pytest
```
Expected: `pyproject.toml` gains a dev dependency group containing `pytest`; `uv` resolves and installs it.

- [ ] **Step 2: Verify pytest runs**

Run: `.venv/bin/pytest --version`
Expected: prints a pytest version (e.g. `pytest 8.x`).

- [ ] **Step 3: Create the tests package + shared fixtures**

Create `tests/__init__.py` (empty).

Create `tests/conftest.py`:
```python
"""Shared pytest fixtures for pipeline hardening tests."""
import socket
from pathlib import Path

import pytest

REPO_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture
def free_port() -> int:
    """Return an OS-assigned free TCP port."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture
def tmp_app_dir(tmp_path: Path) -> Path:
    """An empty app directory under a temp path."""
    d = tmp_path / "app"
    d.mkdir()
    return d
```

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml uv.lock tests/__init__.py tests/conftest.py
git commit -m "test: add pytest scaffolding and shared fixtures"
```

---

### Task 1: `status.py` — STATUS.json, finalize_status, activity log

**Files:**
- Create: `infra/status.py`
- Test: `tests/test_status.py`

This module is the reporting foundation used by every later task.

- [ ] **Step 1: Write failing tests**

Create `tests/test_status.py`:
```python
import json
from pathlib import Path

from infra import status


def _read(p: Path) -> dict:
    return json.loads(p.read_text())


def test_update_activity_appends_line_and_sets_current(tmp_path):
    sr = status.StatusReporter(env="demo", log_dir=tmp_path / "log",
                               output_dir=tmp_path / "out")
    sr.update_activity("Phase 1: generating app")
    sr.update_activity("Phase 1: health gate PASSED")

    log_lines = (tmp_path / "log" / "activity.log").read_text().strip().splitlines()
    assert len(log_lines) == 2
    assert "Phase 1: generating app" in log_lines[0]
    assert "health gate PASSED" in log_lines[1]

    st = _read(tmp_path / "log" / "STATUS.json")
    assert st["current_activity"] == "Phase 1: health gate PASSED"
    assert st["state"] == "RUNNING"


def test_activity_mirrored_to_output(tmp_path):
    sr = status.StatusReporter(env="demo", log_dir=tmp_path / "log",
                               output_dir=tmp_path / "out")
    sr.update_activity("hello")
    assert (tmp_path / "out" / "activity.log").exists()
    assert (tmp_path / "out" / "STATUS.json").exists()


def test_finalize_success_sets_state_and_code(tmp_path):
    sr = status.StatusReporter(env="demo", log_dir=tmp_path / "log",
                               output_dir=tmp_path / "out")
    sr.checkpoint(phase="phase_2b", pass_rate=92.0)
    code = sr.finalize(state="SUCCESS", status_code="SUCCESS")
    st = _read(tmp_path / "log" / "STATUS.json")
    assert st["state"] == "SUCCESS"
    assert st["status_code"] == "SUCCESS"
    assert st["pass_rates"]["phase_2b"] == 92.0
    assert code == 0


def test_finalize_failure_returns_distinct_exit_code(tmp_path):
    sr = status.StatusReporter(env="demo", log_dir=tmp_path / "log",
                               output_dir=tmp_path / "out")
    code = sr.finalize(state="FAILED", status_code="APP_BROKEN",
                       diagnostic="server.py boot error")
    st = _read(tmp_path / "log" / "STATUS.json")
    assert st["state"] == "FAILED"
    assert st["status_code"] == "APP_BROKEN"
    assert st["diagnostic"] == "server.py boot error"
    assert code == status.EXIT_CODES["APP_BROKEN"]
    assert code != 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_status.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'infra.status'` (or `AttributeError`).

- [ ] **Step 3: Implement `infra/status.py`**

Create `infra/status.py`:
```python
"""Per-environment status reporting + live activity log.

Three distinct outputs:
  - pipeline.log  : verbose subprocess output (handled elsewhere)
  - STATUS.json   : structured machine-readable snapshot (this module)
  - activity.log  : human-readable running narrative (this module)

STATUS.json and activity.log are written to both log_dir and output_dir
(the latter mirrors to /output so they survive container teardown).
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

# Distinct, stable exit codes per terminal status class.
EXIT_CODES: dict[str, int] = {
    "SUCCESS": 0,
    "MODEL_UNAVAILABLE": 10,
    "GEN_EMPTY": 11,
    "APP_BROKEN": 12,
    "TASKS_INVALID": 13,
    "EVAL_HARNESS": 14,
    "EVAL_HANG": 15,
    "DISK_FULL": 16,
    "WALL_TIMEOUT": 17,
    "FATAL": 20,
}


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


class StatusReporter:
    """Writes STATUS.json + activity.log to log_dir and (mirrored) output_dir."""

    def __init__(self, env: str, log_dir: Path, output_dir: Path | None = None):
        self.env = env
        self.log_dir = Path(log_dir)
        self.output_dir = Path(output_dir) if output_dir else None
        self.log_dir.mkdir(parents=True, exist_ok=True)
        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        self._state = {
            "env": env,
            "state": "RUNNING",
            "status_code": None,
            "last_phase": None,
            "current_activity": None,
            "diagnostic": None,
            "attempts": {},
            "pass_rates": {},
            "started": _now(),
            "updated": _now(),
        }
        self._write_status()

    # ---- internal ----
    def _targets(self, name: str) -> list[Path]:
        paths = [self.log_dir / name]
        if self.output_dir:
            paths.append(self.output_dir / name)
        return paths

    def _write_status(self) -> None:
        self._state["updated"] = _now()
        blob = json.dumps(self._state, indent=2)
        for p in self._targets("STATUS.json"):
            p.write_text(blob)

    # ---- public API ----
    def update_activity(self, msg: str) -> None:
        """Append a timestamped narrative line and set current_activity."""
        line = f"{datetime.now().strftime('%H:%M:%S')}  {msg}\n"
        for p in self._targets("activity.log"):
            with open(p, "a") as f:
                f.write(line)
        self._state["current_activity"] = msg
        self._write_status()

    def checkpoint(self, phase: str | None = None, *, pass_rate: float | None = None,
                   attempt_key: str | None = None) -> None:
        """Update last_phase / pass_rates / attempt counters mid-run."""
        if phase is not None:
            self._state["last_phase"] = phase
            if pass_rate is not None:
                self._state["pass_rates"][phase] = pass_rate
        if attempt_key is not None:
            self._state["attempts"][attempt_key] = \
                self._state["attempts"].get(attempt_key, 0) + 1
        self._write_status()

    def finalize(self, *, state: str, status_code: str,
                 diagnostic: str | None = None) -> int:
        """Write terminal status and return the process exit code."""
        self._state["state"] = state
        self._state["status_code"] = status_code
        if diagnostic is not None:
            self._state["diagnostic"] = diagnostic
        self._write_status()
        return EXIT_CODES.get(status_code, EXIT_CODES["FATAL"])
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/test_status.py -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
git add infra/status.py tests/test_status.py
git commit -m "feat: status reporter with STATUS.json and live activity log"
```

---

### Task 2: `recovery.py` — error classification + backoff + deployment fallback

**Files:**
- Create: `infra/recovery.py`
- Test: `tests/test_recovery.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_recovery.py`:
```python
import pytest

from infra import recovery


def test_classify_429():
    assert recovery.classify_error("HTTP 429 Too Many Requests") == "RATE_LIMIT"


def test_classify_5xx():
    assert recovery.classify_error("502 Bad Gateway") == "SERVER_ERROR"
    assert recovery.classify_error("InternalServerError 500") == "SERVER_ERROR"


def test_classify_connection():
    assert recovery.classify_error("Connection reset by peer") == "CONNECTION"
    assert recovery.classify_error("read timed out") == "CONNECTION"


def test_classify_unknown_defaults_to_server_error():
    assert recovery.classify_error("weird unparseable text") == "SERVER_ERROR"


def test_backoff_schedule_rate_limit_caps_at_120():
    waits = [recovery.backoff_seconds("RATE_LIMIT", a, jitter=False) for a in range(1, 9)]
    assert waits[0] == 5
    assert waits == sorted(waits)        # monotonic non-decreasing
    assert max(waits) <= 120             # capped


def test_max_attempts_per_class():
    assert recovery.MAX_ATTEMPTS["RATE_LIMIT"] == 8
    assert recovery.MAX_ATTEMPTS["SERVER_ERROR"] == 4
    assert recovery.MAX_ATTEMPTS["CONNECTION"] == 3


def test_jitter_within_bounds(monkeypatch):
    # full jitter => result in [0, computed]
    monkeypatch.setattr(recovery.random, "random", lambda: 1.0)
    hi = recovery.backoff_seconds("RATE_LIMIT", 2, jitter=True)
    monkeypatch.setattr(recovery.random, "random", lambda: 0.0)
    lo = recovery.backoff_seconds("RATE_LIMIT", 2, jitter=True)
    assert lo == 0
    assert hi == recovery.backoff_seconds("RATE_LIMIT", 2, jitter=False)


def test_deployment_list_defaults_to_single():
    assert recovery.deployments("eval", config={}) == [recovery.DEFAULT_EVAL_MODEL]


def test_deployment_list_uses_config():
    cfg = {"EVAL_DEPLOYMENTS": ["a", "b"]}
    assert recovery.deployments("eval", config=cfg) == ["a", "b"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_recovery.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'infra.recovery'`.

- [ ] **Step 3: Implement `infra/recovery.py`**

Create `infra/recovery.py`:
```python
"""Error classification, backoff schedule, and deployment-fallback config.

Light, defensive retry policy (the target environment is ~5 jobs, no quota).
Used by pipeline.py's phase wrappers. Deployment fallback is config-driven and
dormant when only one deployment is configured per model.
"""
from __future__ import annotations

import random

DEFAULT_EVAL_MODEL = "deepseek-v32-az"
DEFAULT_GEN_MODEL = "litellm/aws/glm-5"

MAX_ATTEMPTS = {
    "RATE_LIMIT": 8,
    "SERVER_ERROR": 4,
    "CONNECTION": 3,
}

# base*2**(attempt-1), capped
_BACKOFF = {
    "RATE_LIMIT": {"base": 5, "cap": 120},
    "SERVER_ERROR": {"base": 5, "cap": 80},
    "CONNECTION": {"base": 3, "cap": 60},
}


def classify_error(text: str) -> str:
    """Map an error string to RATE_LIMIT | SERVER_ERROR | CONNECTION."""
    t = (text or "").lower()
    if "429" in t or "rate limit" in t or "too many requests" in t or "overloaded" in t:
        return "RATE_LIMIT"
    if any(k in t for k in ("connection", "timed out", "timeout", "reset", "broken pipe")):
        return "CONNECTION"
    if any(k in t for k in ("500", "502", "503", "504", "server error", "internalservererror")):
        return "SERVER_ERROR"
    return "SERVER_ERROR"  # safe default: moderate retry


def backoff_seconds(error_class: str, attempt: int, *, jitter: bool = True) -> int:
    """Exponential backoff (seconds) for a given error class and 1-based attempt.

    With jitter=True applies full jitter: a random value in [0, computed].
    """
    cfg = _BACKOFF.get(error_class, _BACKOFF["SERVER_ERROR"])
    raw = cfg["base"] * (2 ** (attempt - 1))
    capped = min(raw, cfg["cap"])
    if jitter:
        return int(capped * random.random())
    return capped


def deployments(kind: str, config: dict) -> list[str]:
    """Ordered deployment list for 'eval' or 'gen'. Defaults to a single model."""
    if kind == "eval":
        return list(config.get("EVAL_DEPLOYMENTS") or [DEFAULT_EVAL_MODEL])
    if kind == "gen":
        return list(config.get("GEN_DEPLOYMENTS") or [DEFAULT_GEN_MODEL])
    raise ValueError(f"unknown deployment kind: {kind}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/test_recovery.py -v`
Expected: PASS (8 passed).

- [ ] **Step 5: Commit**

```bash
git add infra/recovery.py tests/test_recovery.py
git commit -m "feat: error classification, backoff schedule, deployment config"
```

---

### Task 3: `app_health.py` — functional smoke test (boot + endpoints + browser load)

**Files:**
- Create: `infra/app_health.py`
- Test: `tests/test_app_health.py`
- Test fixtures: `tests/fixtures/` (good + broken apps, created by the test)

This is the highest-value module: it observes only, never edits, and returns `(ok, diagnostic)`.

- [ ] **Step 1: Write failing tests (with inline fixture apps)**

Create `tests/test_app_health.py`:
```python
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
                self.send_response(200); self.end_headers(); self.wfile.write(b'{"status":"ok"}')
            else: self.send_error(404)
        def do_POST(self):
            global _state
            if self.path=="/api/reset":
                with _lock: _state=json.loads(json.dumps(_seed)) if _seed else None
                self.send_response(200); self.end_headers(); self.wfile.write(b'{"status":"ok"}')
            else: self.send_error(404)
        def do_GET(self):
            if self.path=="/api/state":
                with _lock: s=_state
                if s is None: self.send_response(404); self.end_headers(); self.wfile.write(b'{}')
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_app_health.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'infra.app_health'`.

- [ ] **Step 3: Implement `infra/app_health.py`**

Create `infra/app_health.py`:
```python
"""Functional app health gate. OBSERVE-ONLY — never edits app files.

Returns (ok: bool, diagnostic: str). The diagnostic is a structured, size-capped
string of real evidence (server stderr, HTTP mismatch, JS console errors) suitable
for feeding straight into the fix-app-health model prompt.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import requests

# Reuse the eval harness server lifecycle helpers.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "evaluation"))
from server import kill_port, start_server, stop_server, wait_for_server  # noqa: E402

DIAG_CAP = 3000          # max chars of diagnostic fed to the model
BROWSER_SETTLE_S = 3     # time to let JS run and PUT state


def _structural(app_dir: Path) -> str | None:
    missing = []
    for name in ("server.py", "index.html"):
        if not (app_dir / name).is_file():
            missing.append(name)
    if not (app_dir / "js").is_dir() or not list((app_dir / "js").glob("*.js")):
        missing.append("js/*.js")
    if not (app_dir / "css").is_dir() or not list((app_dir / "css").glob("*.css")):
        missing.append("css/*.css")
    if missing:
        return "Structural check failed — missing required files: " + ", ".join(missing)
    return None


def _endpoints(base: str) -> str | None:
    # GET /api/state -> 404 before any push (by design)
    r = requests.get(f"{base}/api/state", timeout=5)
    if r.status_code != 404:
        return f"GET /api/state before any PUT returned {r.status_code}, expected 404"
    # PUT /api/state -> 200
    r = requests.put(f"{base}/api/state", json={"_health": 1}, timeout=5)
    if r.status_code != 200:
        return f"PUT /api/state returned {r.status_code}, expected 200; body: {r.text[:200]}"
    # GET /api/state -> 200 and echoes
    r = requests.get(f"{base}/api/state", timeout=5)
    if r.status_code != 200 or r.json().get("_health") != 1:
        return f"GET /api/state after PUT returned {r.status_code}; body: {r.text[:200]}"
    # POST /api/reset -> 200
    r = requests.post(f"{base}/api/reset", timeout=5)
    if r.status_code != 200:
        return f"POST /api/reset returned {r.status_code}, expected 200; body: {r.text[:200]}"
    return None


def _browser_load(app_dir: Path, port: int, base: str) -> str | None:
    """Load index.html in a real headless browser; confirm the app's own JS PUT state.

    Captures console errors / uncaught exceptions for the diagnostic.
    """
    from playwright.sync_api import sync_playwright

    # Reset server state so we only see what THIS load pushes.
    requests.post(f"{base}/api/reset", timeout=5)
    console_errors: list[str] = []
    page_errors: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        try:
            page.goto(f"{base}/index.html", timeout=15000)
        except Exception as exc:  # navigation failure
            browser.close()
            return f"Browser failed to load index.html: {exc}"
        time.sleep(BROWSER_SETTLE_S)
        browser.close()

    r = requests.get(f"{base}/api/state", timeout=5)
    if r.status_code == 200 and r.json():
        return None  # app JS pushed state — healthy
    detail = ""
    if page_errors:
        detail = " | uncaught JS errors: " + " ;; ".join(page_errors[:5])
    elif console_errors:
        detail = " | console errors: " + " ;; ".join(console_errors[:5])
    return ("After loading index.html the app's JS did not PUT state "
            f"(GET /api/state returned {r.status_code})." + detail)


def run_health_gate(app_dir: Path, port: int) -> tuple[bool, str]:
    """Run the full gate. Returns (ok, diagnostic). Never edits files."""
    app_dir = Path(app_dir)

    struct = _structural(app_dir)
    if struct:
        return False, struct[:DIAG_CAP]

    proc = start_server(str(app_dir), port)
    base = f"http://localhost:{port}"
    try:
        if not wait_for_server(port, timeout=10):
            err = b""
            if proc.poll() is not None and proc.stderr:
                err = proc.stderr.read() or b""
            return False, (f"server.py did not start / never bound on :{port} "
                           f"(boot). stderr: {err.decode(errors='replace')[-1500:]}")[:DIAG_CAP]
        ep = _endpoints(base)
        if ep:
            return False, ep[:DIAG_CAP]
        br = _browser_load(app_dir, port, base)
        if br:
            return False, br[:DIAG_CAP]
        return True, "health gate passed"
    finally:
        stop_server(proc)
        kill_port(port)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/test_app_health.py -v`
Expected: PASS (4 passed). If Playwright complains the browser is missing, run `.venv/bin/playwright install chromium` once, then re-run.

- [ ] **Step 5: Commit**

```bash
git add infra/app_health.py tests/test_app_health.py
git commit -m "feat: functional app health gate (boot + endpoints + browser load)"
```

---

### Task 4: `fix-app-health.md` — model fix-prompt

**Files:**
- Create: `infra/prompts/fix-app-health.md`

- [ ] **Step 1: Create the prompt template**

Create `infra/prompts/fix-app-health.md`:
```markdown
The generated app at `apps/{app-name}` FAILED its functional health check.

Here is exactly what failed (real evidence captured by the checker):

```
{diagnostics}
```

Fix ONLY the responsible file(s) so the app passes the health check. The health
check, in order, verifies:
1. Required files exist (`server.py`, `index.html`, `js/*.js`, `css/*.css`).
2. `server.py` starts and binds its port.
3. `GET /api/state` returns 404 before any push; `PUT /api/state` returns 200;
   `GET /api/state` then returns 200 with the same JSON; `POST /api/reset` returns 200.
4. When `index.html` is loaded in a browser, the app's own JavaScript PUTs its full
   state to `/api/state` on load.

Do NOT rewrite working parts of the app. Do NOT change `server.py` if the failure is
in the browser JavaScript (most "did not PUT state" failures are JS-init bugs — an
uncaught exception in `app.js`/`state.js`/`views.js` prevents the state push). Make the
smallest change that fixes the reported failure, then stop.
```

- [ ] **Step 2: Verify it loads with the existing template mechanism**

Run:
```bash
.venv/bin/python -c "import sys; sys.path.insert(0,'infra'); \
from pipeline import load_prompt; \
print(load_prompt('fix-app-health', **{'app-name':'demo','diagnostics':'server.py boot error'})[:120])"
```
Expected: prints the filled template head with `apps/demo` and the diagnostics interpolated (no `KeyError`).

- [ ] **Step 3: Commit**

```bash
git add infra/prompts/fix-app-health.md
git commit -m "feat: fix-app-health model prompt carrying health-gate diagnostics"
```

---

### Task 5: `cleanup_results.py` — standalone safe disk cleanup + shared free-space helper

**Files:**
- Create: `infra/cleanup_results.py`
- Test: `tests/test_cleanup_results.py`

Runs OUTSIDE any live pipeline. Also exposes `free_gb()` reused by the in-job disk check.

- [ ] **Step 1: Write failing tests**

Create `tests/test_cleanup_results.py`:
```python
import json
import time
from pathlib import Path

from infra import cleanup_results as cr


def _env(root: Path, name: str, state: str, age_hours: float = 100):
    d = root / name
    d.mkdir(parents=True)
    (d / "data.txt").write_text("x" * 100)
    st = {"env": name, "state": state}
    (d / "STATUS.json").write_text(json.dumps(st))
    old = time.time() - age_hours * 3600
    import os
    os.utime(d / "STATUS.json", (old, old))
    return d


def test_free_gb_returns_positive(tmp_path):
    assert cr.free_gb(tmp_path) > 0


def test_dry_run_lists_but_deletes_nothing(tmp_path):
    _env(tmp_path, "stale-done", state="SUCCESS")
    plan = cr.plan_cleanup(tmp_path, min_age_hours=24)
    assert any("stale-done" in str(p) for p in plan)
    cr.run_cleanup(tmp_path, min_age_hours=24, dry_run=True)
    assert (tmp_path / "stale-done").exists()  # nothing deleted in dry-run


def test_active_env_is_skipped(tmp_path):
    _env(tmp_path, "running-now", state="RUNNING", age_hours=0)
    plan = cr.plan_cleanup(tmp_path, min_age_hours=24)
    assert not any("running-now" in str(p) for p in plan)


def test_real_cleanup_backs_up_then_deletes(tmp_path):
    _env(tmp_path, "stale-done", state="SUCCESS")
    backup_dir = tmp_path / "_backups"
    cr.run_cleanup(tmp_path, min_age_hours=24, dry_run=False, backup_dir=backup_dir)
    assert not (tmp_path / "stale-done").exists()        # deleted
    assert list(backup_dir.glob("stale-done*.tar"))      # tar backup exists
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_cleanup_results.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'infra.cleanup_results'`.

- [ ] **Step 3: Implement `infra/cleanup_results.py`**

Create `infra/cleanup_results.py`:
```python
"""Standalone, safe disk cleanup for the results volume.

Runs OUTSIDE any live pipeline. Safety (per project cleanup-trap rule):
  - dry-run by default
  - tar-backup before any delete
  - never deletes an env whose run looks active (STATUS.json state==RUNNING
    or a recent mtime)
Also exposes free_gb() reused by pipeline.py's in-job disk check.

Usage:
    python infra/cleanup_results.py --root /path/to/webarena-results          # dry-run
    python infra/cleanup_results.py --root /path/to/webarena-results --apply  # delete
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path


def free_gb(path: Path) -> float:
    """Free space (GiB) on the filesystem holding *path*."""
    usage = shutil.disk_usage(str(path))
    return usage.free / (1024 ** 3)


def _looks_active(env_dir: Path, min_age_hours: float) -> bool:
    status = env_dir / "STATUS.json"
    if status.exists():
        try:
            if json.loads(status.read_text()).get("state") == "RUNNING":
                return True
        except (json.JSONDecodeError, OSError):
            return True  # unreadable → treat as active (safe)
        age_h = (time.time() - status.stat().st_mtime) / 3600
        return age_h < min_age_hours
    # No STATUS.json: fall back to directory mtime
    age_h = (time.time() - env_dir.stat().st_mtime) / 3600
    return age_h < min_age_hours


def plan_cleanup(root: Path, min_age_hours: float = 24) -> list[Path]:
    """Return env dirs eligible for deletion (stale + not active)."""
    root = Path(root)
    eligible = []
    for d in sorted(root.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        if _looks_active(d, min_age_hours):
            continue
        eligible.append(d)
    return eligible


def run_cleanup(root: Path, *, min_age_hours: float = 24, dry_run: bool = True,
                backup_dir: Path | None = None) -> list[Path]:
    """Tar-backup then delete eligible dirs. Returns the dirs acted on."""
    root = Path(root)
    backup_dir = Path(backup_dir) if backup_dir else root / "_backups"
    targets = plan_cleanup(root, min_age_hours)
    for d in targets:
        if dry_run:
            print(f"[dry-run] would back up + delete: {d}")
            continue
        backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        tar = backup_dir / f"{d.name}_{stamp}.tar"
        subprocess.run(["tar", "-cf", str(tar), "-C", str(root), d.name],
                       check=True, timeout=600)
        if tar.stat().st_size == 0:
            print(f"[skip] backup empty, NOT deleting: {d}")
            continue
        shutil.rmtree(d)
        print(f"[deleted] {d} (backup: {tar})")
    return targets


def main() -> None:
    ap = argparse.ArgumentParser(description="Safe results-volume cleanup")
    ap.add_argument("--root", required=True)
    ap.add_argument("--min-age-hours", type=float, default=24)
    ap.add_argument("--apply", action="store_true", help="actually delete (default: dry-run)")
    ap.add_argument("--backup-dir", default=None)
    a = ap.parse_args()
    print(f"Free space on {a.root}: {free_gb(Path(a.root)):.1f} GiB")
    run_cleanup(Path(a.root), min_age_hours=a.min_age_hours,
                dry_run=not a.apply,
                backup_dir=Path(a.backup_dir) if a.backup_dir else None)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/test_cleanup_results.py -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
git add infra/cleanup_results.py tests/test_cleanup_results.py
git commit -m "feat: standalone safe results-volume cleanup + free_gb helper"
```

---

### Task 6: Tier-1 eval LLM-client backoff in `run_eval_parallel.py`

**Files:**
- Modify: `evaluation/run_eval_parallel.py` (the `AGENT_FACTORIES` ChatOpenAI constructions)

The eval agent makes per-step LLM calls; absorbing transient errors there keeps a single hiccup from failing a task.

- [ ] **Step 1: Confirm the LLM client's supported retry kwargs**

Run:
```bash
.venv/bin/python -c "import inspect; from browser_use.llm.openai.chat import ChatOpenAI; \
print([p for p in inspect.signature(ChatOpenAI).parameters])"
```
Expected: prints the constructor parameter names. Look for `max_retries` and `timeout` (browser_use's ChatOpenAI mirrors the OpenAI client). Note which of the two exist.

- [ ] **Step 2: Add a small factory helper that injects the supported kwargs**

In `evaluation/run_eval_parallel.py`, just above the `AGENT_FACTORIES` dict, add:
```python
# Per-request resilience: let the LLM client retry transient errors itself so a
# single hiccup doesn't fail a whole task. Only pass kwargs the client supports.
import inspect as _inspect

def _chat_openai(model: str):
    from browser_use.llm.openai.chat import ChatOpenAI
    kwargs = {"model": model}
    params = _inspect.signature(ChatOpenAI).parameters
    if "max_retries" in params:
        kwargs["max_retries"] = 6
    if "timeout" in params:
        kwargs["timeout"] = 120
    return ChatOpenAI(**kwargs)
```

- [ ] **Step 3: Route the OpenAI-compatible factories through the helper**

In `evaluation/run_eval_parallel.py`, replace each `lambda: __import__(...).ChatOpenAI(model="X")`
for the OpenAI-compatible eval models (`gpt`, `qwen`, `gpt-oss`, `dsv4pro`, `deepseek-v32`,
`deepseek-v32-az`, `glmv5.1`) with `lambda: _chat_openai("X")`. For example:
```python
    "deepseek-v32-az": lambda **kw: _make_browser_use_agent(
        lambda: _chat_openai("azure/DeepSeek-V3.2"), **kw),
```
(Leave Google/Anthropic and vision factories unchanged.)

- [ ] **Step 4: Smoke-check the module still imports and builds a factory**

Run:
```bash
.venv/bin/python -c "import sys; sys.path.insert(0,'evaluation'); \
import run_eval_parallel as r; print('deepseek-v32-az' in r.AGENT_FACTORIES)"
```
Expected: prints `True` with no import error.

- [ ] **Step 5: Commit**

```bash
git add evaluation/run_eval_parallel.py
git commit -m "feat: per-request retry/timeout on eval LLM client (tier-1 backoff)"
```

---

### Task 7: Wire generation hardening into `pipeline.py`

**Files:**
- Modify: `infra/pipeline.py`

Add helpers and route generation phases through them. The model still authors all code.

- [ ] **Step 1: Add imports + a module-level StatusReporter handle**

Near the top of `infra/pipeline.py` (after existing imports), add:
```python
from app_health import run_health_gate
from recovery import classify_error, backoff_seconds, MAX_ATTEMPTS, deployments
from status import StatusReporter, EXIT_CODES
from cleanup_results import free_gb

# Tunables (config-driven; safe defaults)
GEN_REGEN_BUDGET = 3
MIN_FREE_GB = 5.0
DEPLOYMENT_CONFIG: dict = {}   # populate EVAL_DEPLOYMENTS / GEN_DEPLOYMENTS to enable fallback

reporter: "StatusReporter | None" = None   # set in main()
```
(`infra/` is already on `sys.path` because `pipeline.py` runs from there; the existing
`from upload_results import ...` pattern confirms sibling imports work.)

- [ ] **Step 2: Add a `disk_guard()` detect-only helper**

Add to `infra/pipeline.py`:
```python
def disk_guard(app_dir: Path, phase: str) -> None:
    """Read-only disk check. NEVER deletes (preserves crash-recovery backups).

    If free space is below MIN_FREE_GB, finalize a DISK_FULL status and exit cleanly.
    """
    target = Path("/output") if Path("/output").is_dir() else app_dir
    gb = free_gb(target)
    if gb < MIN_FREE_GB:
        msg = f"Disk near-full on {target}: {gb:.1f} GiB free (< {MIN_FREE_GB})"
        log.error(msg)
        if reporter:
            reporter.update_activity(f"{phase}: ABORTING — {msg}")
            code = reporter.finalize(state="FAILED", status_code="DISK_FULL", diagnostic=msg)
        else:
            code = EXIT_CODES["DISK_FULL"]
        sys.exit(code)
```

- [ ] **Step 3: Add an `app_health_gate_with_fix()` helper (gate → model fix → re-gate)**

Add to `infra/pipeline.py`:
```python
def app_health_gate_with_fix(app_dir: Path, args, phase: str, base_port: int) -> bool:
    """Run the health gate; on failure, have the MODEL fix it (bounded). Returns True if healthy.

    The pipeline never edits app files — only re-invokes the model with diagnostics.
    """
    health_port = base_port + 90   # avoid eval worker ports
    for attempt in range(1, GEN_REGEN_BUDGET + 1):
        ok, diag = run_health_gate(app_dir, port=health_port)
        if ok:
            if reporter:
                reporter.update_activity(f"{phase}: health gate PASSED")
            return True
        log.warning("Health gate failed (attempt %d/%d): %s", attempt, GEN_REGEN_BUDGET, diag)
        if reporter:
            reporter.update_activity(
                f"{phase}: health gate FAILED — {diag[:120]}")
            reporter.checkpoint(attempt_key=f"{phase}_regen")
        if attempt == GEN_REGEN_BUDGET:
            break
        if reporter:
            reporter.update_activity(
                f"{phase}: asking model to fix app (attempt {attempt + 1}/{GEN_REGEN_BUDGET})")
        run_agent(
            "fix-app-health",
            cwd=REPO_DIR,
            timeout=10800,
            agent=args.agent,
            generation_model=args.generation_model,
            app_name=args.app_name,
            diagnostics=diag,
            **{"app-name": args.app_name},
        )
    return False
```

- [ ] **Step 4: Initialize the reporter in `main()`**

In `main()`, immediately after `log = setup_logging(args.app_name)`, add:
```python
    global reporter
    _out = Path("/output") / args.app_name if Path("/output").is_dir() else None
    reporter = StatusReporter(env=args.app_name,
                              log_dir=REPO_DIR / "logs" / args.app_name,
                              output_dir=_out)
    reporter.update_activity("Pipeline starting")
```

- [ ] **Step 5: Gate Phase 1 after generation**

In `main()`, in the Phase 1 block, immediately AFTER the existing
`validate_app_generation` success path and BEFORE `log.info("Phase 1 complete...")`,
add:
```python
        if not app_health_gate_with_fix(app_dir, args, "phase_1", args.base_port):
            code = reporter.finalize(state="FAILED", status_code="APP_BROKEN",
                                     diagnostic="health gate failed after regenerate budget")
            sys.exit(code)
```

- [ ] **Step 6: Add disk_guard + activity at each phase boundary**

In `main()`, at the start of each phase block (Phase 1, 2a, 2b, 3a, 3b, 4, 5), add a
line mirroring the phase, e.g. at the top of the Phase 1 block:
```python
        disk_guard(app_dir, "phase_1")
        reporter.update_activity("Phase 1: generating app")
```
Repeat with the correct phase label for 2a/2b/3a/3b/4/5 (the executor reads each phase's
existing `log.info("Phase N...")` line and inserts the matching pair just below it).

- [ ] **Step 7: Re-gate after audits that modify app code**

After each audit's `commit_checkpoint(...)` in Phases 2b, 3b, and 4 (where
`detect_changes(app_dir)` was true and the app may have changed), add:
```python
            if not app_health_gate_with_fix(app_dir, args, "phase_2b", args.base_port):
                code = reporter.finalize(state="FAILED", status_code="APP_BROKEN",
                                         diagnostic="app broke after audit")
                sys.exit(code)
```
(Use the matching phase label `phase_3b` / `phase_4b` at the other two sites.)

- [ ] **Step 8: Wrap the pipeline body in a top-level safety net + success finalize**

Wrap the existing body of `main()` (from after argument parsing/reporter init through the
end) in:
```python
    try:
        ...  # existing phase pipeline
        reporter.finalize(state="SUCCESS", status_code="SUCCESS")
        log.info("Pipeline complete for: %s", args.app_name)
    except SystemExit:
        raise  # already finalized with a classified code
    except BaseException as exc:  # noqa: BLE001 — last-resort net
        import traceback
        tb = traceback.format_exc()[-3000:]
        log.error("FATAL uncaught exception: %s", exc)
        code = reporter.finalize(state="FAILED", status_code="FATAL", diagnostic=tb)
        sys.exit(code)
```

- [ ] **Step 9: Verify the module imports and `--help` works**

Run: `.venv/bin/python infra/pipeline.py --help`
Expected: argparse help prints with no ImportError from the new modules.

- [ ] **Step 10: Commit**

```bash
git add infra/pipeline.py
git commit -m "feat: wire health gate, disk guard, status + activity into generation phases"
```

---

### Task 8: Eval-phase hardening (watchdog + 0-task routing via health gate) in `pipeline.py`

**Files:**
- Modify: `infra/pipeline.py`

The existing 0-task retry stays; we add health-gate routing and a hang watchdog, and emit
activity + classified exits.

- [ ] **Step 1: Route persistent eval 0/0 through the health gate**

In each eval phase (2b/3b) where the code currently retries on `results["total"] == 0`
and then `sys.exit(1)`, replace the final `sys.exit(1)` with health-gate routing:
```python
                if results["total"] == 0:
                    ok, diag = run_health_gate(app_dir, port=args.base_port + 90)
                    if not ok:
                        reporter.update_activity(f"{phase_label}: eval 0/0 — app broken; "
                                                 "regenerating")
                        # broken app: hand back to Phase-1 regeneration budget
                        if not app_health_gate_with_fix(app_dir, args, phase_label, args.base_port):
                            code = reporter.finalize(state="FAILED", status_code="APP_BROKEN",
                                                     diagnostic=diag)
                            sys.exit(code)
                    else:
                        code = reporter.finalize(state="FAILED", status_code="EVAL_HARNESS",
                                                 diagnostic="eval returned 0 tasks but app is healthy")
                        sys.exit(code)
```
(`phase_label` is `"phase_2b"` / `"phase_3b"` at the respective sites.)

- [ ] **Step 2: Add an eval hang watchdog**

The existing `run_eval` already enforces a 12h deadline and kills the subprocess. Make the
kill robust against orphaned children by killing the whole process group. In `run_eval`,
where `proc = subprocess.Popen(cmd, ...)` is created, add `start_new_session=True`, and in
the `TimeoutExpired` handler replace `proc.kill()` with:
```python
        import os, signal as _signal
        try:
            os.killpg(os.getpgid(proc.pid), _signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            proc.kill()
```
When this fires, set the resulting status via the caller: after `run_eval` returns its
timeout sentinel, if no results were produced, `reporter.finalize(state="FAILED",
status_code="EVAL_HANG", ...)` and exit. (The executor adds the caller-side check next to
the existing `find_latest_results` fallback.)

- [ ] **Step 3: Emit pass-rate activity + checkpoint after each eval**

After each eval's `parse_results(...)` in 2b/3b/4b/5, add:
```python
            reporter.checkpoint(phase=phase_label, pass_rate=results["pass_rate"])
            reporter.update_activity(
                f"{phase_label}: pass rate {results['pass_rate']}% "
                f"({results['passed']}/{results['total']})")
```

- [ ] **Step 4: Replace remaining bare `sys.exit(1)` in eval phases with classified exits**

For Phase 4b's `sys.exit(1)` on 0 tasks and Phase 5's `sys.exit(1)` on 0 tasks, replace
with:
```python
            code = reporter.finalize(state="FAILED", status_code="EVAL_HARNESS",
                                     diagnostic="eval returned 0 tasks")
            sys.exit(code)
```

- [ ] **Step 5: Verify import + help still work**

Run: `.venv/bin/python infra/pipeline.py --help`
Expected: prints help, no errors.

- [ ] **Step 6: Run the full unit suite**

Run: `.venv/bin/pytest tests/ -v`
Expected: all tests from Tasks 1–5 PASS.

- [ ] **Step 7: Commit**

```bash
git add infra/pipeline.py
git commit -m "feat: eval-phase hardening (health-gate routing, hang watchdog, classified exits)"
```

---

### Task 9: End-to-end dry verification (manual, optional but recommended)

**Files:** none (verification only)

- [ ] **Step 1: Health gate on a known-good reference app**

Run:
```bash
.venv/bin/python -c "import sys; sys.path.insert(0,'infra'); \
from app_health import run_health_gate; \
print(run_health_gate('apps/linear-account-settings', 8801))"
```
Expected: `(True, 'health gate passed')` (the gold-standard reference app is healthy).

- [ ] **Step 2: Cleanup tool dry-run against a scratch dir**

Run:
```bash
mkdir -p /tmp/wa-clean/old-env && echo x > /tmp/wa-clean/old-env/data.txt
.venv/bin/python infra/cleanup_results.py --root /tmp/wa-clean
```
Expected: prints free space and `[dry-run] would back up + delete: /tmp/wa-clean/old-env`; nothing deleted.

- [ ] **Step 3: Confirm STATUS.json + activity.log are produced on a real (or `--help`) run**

After any real pipeline run, confirm `logs/<app>/STATUS.json` and
`logs/<app>/activity.log` exist and reflect the run. No commit (verification only).

---

## Self-Review

**Spec coverage:**
- Error taxonomy/action vocabulary → Tasks 2,7,8 (classify+backoff, generation routing, eval routing, classified exits via `EXIT_CODES`).
- Same-model deployment fallback (config-driven, dormant) → Task 2 (`deployments()`, `DEPLOYMENT_CONFIG`).
- Tier-1 + Tier-2 backoff → Task 6 (tier-1 client) + Tasks 2/7 (tier-2 schedule/budgets).
- App health gate (boot+endpoints+browser) observe-only → Task 3; model-driven fix → Task 4 + Task 7 Step 3; gate after gen + audits → Task 7 Steps 5/7.
- Diagnostics flow to model → Task 3 (assembled, capped) + Task 4 (prompt) + Task 7 Step 3 (passed via `diagnostics=`).
- Disk: in-job detect-only never deletes → Task 7 Step 2; standalone safe cleanup → Task 5.
- STATUS.json + classified exit codes → Task 1; wired → Tasks 7/8.
- Live activity log + `current_activity` → Task 1; wired at every transition → Tasks 7/8.
- Top-level safety net / no ambiguous crash or hang → Task 7 Step 8 + Task 8 Step 2.
- Invariant (only the model edits code; orphan housekeeping kept) → Task 7 Step 3 (model fix only); existing orphan cleanup untouched.

**Placeholder scan:** no TBD/TODO; every code step contains complete code; integration steps name exact insertion points and the executor reads the current line to place them.

**Type/name consistency:** `StatusReporter.update_activity/checkpoint/finalize`, `EXIT_CODES`, `run_health_gate(app_dir, port) -> (ok, diag)`, `classify_error`, `backoff_seconds`, `deployments`, `free_gb`, `run_cleanup/plan_cleanup` are used consistently across tasks.

**Known follow-ups (out of scope, noted):** external supervisor / job resubmission; the from-scratch new codebase (sub-project 2).
