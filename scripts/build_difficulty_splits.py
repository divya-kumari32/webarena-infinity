#!/usr/bin/env python3
"""
Write per-env difficulty split files: easy.json, medium.json, hard.json.

Output structure (under --out-dir, default: scripts/difficulty_splits/):
    <out_dir>/
        <env_name>/
            easy.json
            medium.json
            hard.json
            all.json        # same as real-tasks.json, for convenience

Usage:
    # Build splits for all envs
    python scripts/build_difficulty_splits.py

    # Build splits for specific envs only
    python scripts/build_difficulty_splits.py --env xero-invoicing gitlab-plan-and-track

    # Custom output directory
    python scripts/build_difficulty_splits.py --out-dir /tmp/splits
"""

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
APPS_DIR = REPO_ROOT / "apps"
DEFAULT_OUT_DIR = Path(__file__).resolve().parent / "difficulty_splits"

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

DIFFICULTIES = ("easy", "medium", "hard")


def build_splits(env_name: str, out_dir: Path) -> dict:
    src = APPS_DIR / env_name / "real-tasks.json"
    if not src.exists():
        print(f"  [SKIP] {env_name}: no real-tasks.json found")
        return {}

    with open(src) as f:
        tasks = json.load(f)

    env_out = out_dir / env_name
    env_out.mkdir(parents=True, exist_ok=True)

    counts = {}
    for diff in DIFFICULTIES:
        subset = [t for t in tasks if t.get("difficulty") == diff]
        out_path = env_out / f"{diff}.json"
        with open(out_path, "w") as f:
            json.dump(subset, f, indent=2)
        counts[diff] = len(subset)

    all_path = env_out / "all.json"
    with open(all_path, "w") as f:
        json.dump(tasks, f, indent=2)
    counts["total"] = len(tasks)

    return counts


def main():
    parser = argparse.ArgumentParser(description="Build easy/medium/hard task split files for each env")
    parser.add_argument(
        "--env",
        nargs="+",
        default=None,
        help="Specific env(s) to process. Defaults to all envs.",
    )
    parser.add_argument(
        "--out-dir",
        default=str(DEFAULT_OUT_DIR),
        help=f"Output directory. Default: {DEFAULT_OUT_DIR}",
    )
    args = parser.parse_args()

    envs = args.env if args.env else ALL_ENVS
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Writing splits to: {out_dir}\n")
    col = max(len(e) for e in envs) + 2

    for env in envs:
        counts = build_splits(env, out_dir)
        if counts:
            print(
                f"  {env:<{col}}  easy={counts.get('easy', 0)}  "
                f"medium={counts.get('medium', 0)}  hard={counts.get('hard', 0)}  "
                f"total={counts.get('total', 0)}"
            )

    print(f"\nDone. Splits written to {out_dir}/")


if __name__ == "__main__":
    main()
