#!/usr/bin/env python3
"""
Filter each env's real-tasks.json to keep only MEDIUM tasks.

Medium tasks are those with difficulty == 'medium' in real-tasks.json.
Each env has exactly 20 medium tasks.

Output structure under --save_dir:
    <save_dir>/
        <env_name>/
            real-tasks.json   ← medium tasks only

Usage:
    python scripts/filter_medium.py --save_dir scripts/difficulty_splits/medium
    python scripts/filter_medium.py --save_dir scripts/difficulty_splits/medium --env xero-invoicing gitlab-plan-and-track
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from filter_utils import ALL_ENVS, filter_and_save, print_report


def main():
    parser = argparse.ArgumentParser(
        description="Filter env tasks to keep only MEDIUM tasks (difficulty == 'medium')."
    )
    parser.add_argument(
        "--save_dir",
        required=True,
        help="Directory to write filtered real-tasks.json files into.",
    )
    parser.add_argument(
        "--env",
        nargs="+",
        default=None,
        help=f"Specific env(s) to process. Default: all {len(ALL_ENVS)} envs.",
    )
    args = parser.parse_args()

    envs = args.env or ALL_ENVS
    print(f"Filtering MEDIUM tasks for {len(envs)} env(s) → {args.save_dir}")

    env_counts = filter_and_save("medium", args.save_dir, envs)
    print_report(env_counts, "medium")
    print(f"Done. Medium task splits written to: {args.save_dir}/")


if __name__ == "__main__":
    main()
