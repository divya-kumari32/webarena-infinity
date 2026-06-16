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
