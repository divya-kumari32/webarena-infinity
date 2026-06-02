"""
Shared utilities for difficulty-based task filtering in WebArena-Infinity.

Each environment's real-tasks.json already carries a 'difficulty' field
(easy / medium / hard) assigned during task generation. These utilities
load, filter, and report on those labeled tasks.

Intended use: called by filter_easy.py / filter_medium.py / filter_hard.py,
mirroring the AWM++ scripts/filter_utils.py interface.
"""

import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Literal

REPO_ROOT = Path(__file__).resolve().parent.parent
APPS_DIR = REPO_ROOT / "apps"

ALL_ENVS = [
    "elation-clinical-records",
    "elation-patient-communication",
    "elation-prescriptions",
    "figma-slides",
    "figma-text-and-typography",
    "gitlab-plan-and-track",
    "gmail",
    "gmail-accounts-and-contacts",
    "handshake-career-exploration",
    "linear-account-settings",
    "paypal-my-wallet",
    "superhuman-general",
    "xero-invoicing",
]

DIFFICULTIES: tuple[str, ...] = ("easy", "medium", "hard")


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_real_tasks(env_name: str) -> list[dict]:
    path = APPS_DIR / env_name / "real-tasks.json"
    if not path.exists():
        raise FileNotFoundError(f"No real-tasks.json for env '{env_name}' at {path}")
    with open(path) as f:
        return json.load(f)


def load_function_tasks(env_name: str) -> list[dict]:
    path = APPS_DIR / env_name / "function-tasks.json"
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def filter_tasks(tasks: list[dict], difficulty: str) -> list[dict]:
    return [t for t in tasks if t.get("difficulty") == difficulty]


# ---------------------------------------------------------------------------
# Saving
# ---------------------------------------------------------------------------

def save_tasks(tasks: list[dict], out_path: str | Path) -> None:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(tasks, f, indent=2)


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_report(env_counts: dict[str, dict[str, int]], difficulty: str) -> None:
    total_envs = len(env_counts)
    total_tasks = sum(c.get(difficulty, 0) for c in env_counts.values())

    col = max(len(e) for e in env_counts) + 2
    print(f"\n{'='*60}")
    print(f"Difficulty Filter Report  —  '{difficulty}'")
    print(f"{'='*60}")
    print(f"  Envs processed : {total_envs}")
    print(f"  Tasks kept     : {total_tasks}")
    print(f"{'='*60}")
    print(f"\n  {'Environment':<{col}}  {'easy':>6}  {'medium':>8}  {'hard':>6}  {'kept':>6}")
    print(f"  {'-'*(col+32)}")
    for env, c in sorted(env_counts.items()):
        kept = c.get(difficulty, 0)
        print(
            f"  {env:<{col}}  {c.get('easy', 0):>6}  {c.get('medium', 0):>8}"
            f"  {c.get('hard', 0):>6}  {kept:>6}"
        )
    print()


def filter_and_save(
    difficulty: Literal["easy", "medium", "hard"],
    save_dir: str | Path,
    envs: list[str] | None = None,
) -> dict[str, dict[str, int]]:
    """
    Filter real-tasks.json for each env to keep only tasks of the given
    difficulty, writing <env>/real-tasks.json into save_dir.

    Returns per-env counts dict for reporting.
    """
    envs = envs or ALL_ENVS
    save_dir = Path(save_dir)
    env_counts: dict[str, dict[str, int]] = {}

    for env in envs:
        try:
            tasks = load_real_tasks(env)
        except FileNotFoundError as e:
            print(f"  [SKIP] {e}")
            continue

        counts: dict[str, int] = defaultdict(int)
        for t in tasks:
            counts[t.get("difficulty", "unknown")] += 1
        env_counts[env] = dict(counts)

        filtered = filter_tasks(tasks, difficulty)
        out_path = save_dir / env / "real-tasks.json"
        save_tasks(filtered, out_path)

    return env_counts
