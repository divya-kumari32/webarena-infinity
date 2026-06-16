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
            return True  # unreadable -> treat as active (safe)
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
