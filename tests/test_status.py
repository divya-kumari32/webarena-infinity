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
