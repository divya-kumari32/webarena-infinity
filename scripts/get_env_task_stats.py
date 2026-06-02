#!/usr/bin/env python3
"""
Print a summary table of all envs and their task counts by difficulty.

Usage:
    python scripts/get_env_task_stats.py
    python scripts/get_env_task_stats.py --env xero-invoicing gitlab-plan-and-track
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

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


def get_stats(env_name: str) -> dict | None:
    path = APPS_DIR / env_name / "real-tasks.json"
    if not path.exists():
        return None
    with open(path) as f:
        tasks = json.load(f)
    counts = defaultdict(int)
    for t in tasks:
        counts[t.get("difficulty", "unknown")] += 1
    return {"easy": counts["easy"], "medium": counts["medium"], "hard": counts["hard"], "total": len(tasks)}


def main():
    parser = argparse.ArgumentParser(description="Show task difficulty stats for all envs")
    parser.add_argument(
        "--env",
        nargs="+",
        default=None,
        help="Specific env(s) to show. Defaults to all envs.",
    )
    args = parser.parse_args()

    envs = args.env if args.env else ALL_ENVS

    col_env = max(len(e) for e in envs) + 2
    header = f"{'Environment':<{col_env}}  {'Easy':>6}  {'Medium':>8}  {'Hard':>6}  {'Total':>7}"
    print(header)
    print("-" * len(header))

    for env in envs:
        stats = get_stats(env)
        if stats is None:
            print(f"{env:<{col_env}}  {'N/A':>6}  {'N/A':>8}  {'N/A':>6}  {'N/A':>7}")
        else:
            print(
                f"{env:<{col_env}}  {stats['easy']:>6}  {stats['medium']:>8}  {stats['hard']:>6}  {stats['total']:>7}"
            )


if __name__ == "__main__":
    main()
