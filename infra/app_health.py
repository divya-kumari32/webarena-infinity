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
    """Load the app in a headless browser via browser_use — the SAME browser stack
    the eval harness uses (see evaluation/agents.py) — and confirm the app's own JS
    PUT state on load. Avoids a hard dependency on Playwright.
    """
    import asyncio

    # Reset server state so we only see what THIS load pushes.
    requests.post(f"{base}/api/reset", timeout=5)

    async def _load() -> None:
        from browser_use import BrowserSession
        try:
            from agents import _EXTRA_CHROME_ARGS  # match eval's container chrome args
        except Exception:
            _EXTRA_CHROME_ARGS = ["--no-sandbox", "--disable-dev-shm-usage"]
        session = BrowserSession(headless=True, keep_alive=True, args=_EXTRA_CHROME_ARGS)
        try:
            await session.start()
            page = await session.get_current_page()
            await page.goto(base)
            await asyncio.sleep(BROWSER_SETTLE_S)
        finally:
            try:
                await session.kill()
            except Exception:
                pass

    try:
        asyncio.run(_load())
    except Exception as exc:  # browser failed to launch / navigate
        return f"Browser failed to load the app via browser_use: {exc}"

    r = requests.get(f"{base}/api/state", timeout=5)
    if r.status_code == 200 and r.json():
        return None  # app JS pushed state — healthy
    return ("After loading index.html the app's JS did not PUT state "
            f"(GET /api/state returned {r.status_code}).")


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
