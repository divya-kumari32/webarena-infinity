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
