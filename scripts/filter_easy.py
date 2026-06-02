#!/usr/bin/env python3
"""
Filter each env's real-tasks.json to keep only EASY tasks.

Easy tasks are those with difficulty == 'easy' in real-tasks.json.
Each env has exactly 20 easy tasks.

Output structure under --save_dir:
    <save_dir>/
        <env_name>/
            real-tasks.json   ← easy tasks only

Usage:
    python scripts/filter_easy.py --save_dir scripts/difficulty_splits/easy
    python scripts/filter_easy.py --save_dir scripts/difficulty_splits/easy --env xero-invoicing gitlab-plan-and-track
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from filter_utils import ALL_ENVS, filter_and_save, print_report


def main():
    parser = argparse.ArgumentParser(
        description="Filter env tasks to keep only EASY tasks (difficulty == 'easy')."
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
    print(f"Filtering EASY tasks for {len(envs)} env(s) → {args.save_dir}")

    env_counts = filter_and_save("easy", args.save_dir, envs)
    print_report(env_counts, "easy")
    print(f"Done. Easy task splits written to: {args.save_dir}/")


if __name__ == "__main__":
    main()
