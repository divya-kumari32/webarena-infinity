#!/usr/bin/env python3
"""
Filter an environment's real-tasks.json by difficulty level(s).

Usage:
    python scripts/filter_tasks_by_difficulty.py <env_name> [--difficulty easy|medium|hard] [--output FILE]

Examples:
    # Print all easy tasks for xero-invoicing
    python scripts/filter_tasks_by_difficulty.py xero-invoicing --difficulty easy

    # Print easy + medium tasks and save to a file
    python scripts/filter_tasks_by_difficulty.py xero-invoicing --difficulty easy medium --output xero_easy_medium.json

    # Print full breakdown (all difficulties, grouped)
    python scripts/filter_tasks_by_difficulty.py xero-invoicing
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
APPS_DIR = REPO_ROOT / "apps"

VALID_DIFFICULTIES = ("easy", "medium", "hard")

# All envs with real-tasks.json (excluding gmail-reproduced and glm-glm5-*)
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


def load_tasks(env_name: str) -> list[dict]:
    path = APPS_DIR / env_name / "real-tasks.json"
    if not path.exists():
        raise FileNotFoundError(f"No real-tasks.json found for env '{env_name}' at {path}")
    with open(path) as f:
        return json.load(f)


def filter_by_difficulty(tasks: list[dict], difficulties: list[str]) -> list[dict]:
    difficulties_set = set(difficulties)
    return [t for t in tasks if t.get("difficulty") in difficulties_set]


def main():
    parser = argparse.ArgumentParser(description="Filter env tasks by difficulty level")
    parser.add_argument("env", help=f"Environment name. One of: {', '.join(ALL_ENVS)}")
    parser.add_argument(
        "--difficulty",
        nargs="+",
        choices=VALID_DIFFICULTIES,
        default=None,
        help="Difficulty level(s) to include. Omit to show all grouped by difficulty.",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output JSON file path. If omitted, prints to stdout.",
    )
    parser.add_argument(
        "--count-only",
        action="store_true",
        help="Print task counts only, not the full task list.",
    )
    args = parser.parse_args()

    try:
        tasks = load_tasks(args.env)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.difficulty:
        filtered = filter_by_difficulty(tasks, args.difficulty)
    else:
        filtered = tasks

    if args.count_only:
        by_diff = defaultdict(int)
        for t in filtered:
            by_diff[t.get("difficulty", "unknown")] += 1
        for d in VALID_DIFFICULTIES:
            print(f"{d}: {by_diff.get(d, 0)}")
        print(f"total: {len(filtered)}")
        return

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w") as f:
            json.dump(filtered, f, indent=2)
        print(f"Wrote {len(filtered)} tasks to {out}", file=sys.stderr)
    else:
        print(json.dumps(filtered, indent=2))


if __name__ == "__main__":
    main()
