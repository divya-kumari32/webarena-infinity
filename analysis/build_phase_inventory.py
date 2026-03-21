#!/usr/bin/env python3
"""
Build a comprehensive phase-by-phase results inventory from all downloaded S3 results.

Walks all results.json files in analysis/s3_results/, extracts metadata,
infers pipeline phase and task type from run folder naming conventions,
and outputs a CSV inventory plus a summary table.

Run folder naming conventions (newest to oldest):
  - gemini-flash_20260318_021439_function-tasks_p2b_parallel   (new: explicit phase)
  - gemini_20260308_005954_p3b_parallel                        (new: explicit phase, real-tasks implied)
  - gemini_20260308_043100_function-tasks_p5_parallel           (new: explicit phase + task type)
  - gemini_20260302_060228_function-tasks_parallel              (old: no phase label)
  - gemini_20260228_023457_parallel                             (old: no phase, no task type label)
  - gemini_20260226_075851_real-tasks_parallel                  (old: explicit real-tasks)
"""

import csv
import json
import os
import re
import sys
from pathlib import Path
from collections import defaultdict

S3_RESULTS_DIR = Path(__file__).parent / "s3_results"
OUTPUT_CSV = S3_RESULTS_DIR / "phase_inventory.csv"

# Regex to parse run folder names
# Format: {model}_{date}_{time}_{...suffixes...}
# Examples:
#   gemini-flash_20260318_021439_function-tasks_p2b_parallel
#   gemini_20260308_005954_p3b_parallel
#   gemini_20260226_075851_real-tasks_parallel
RUN_FOLDER_RE = re.compile(
    r'^(?P<model>[a-z][a-z0-9-]*)'        # model name (e.g. gemini, gemini-pro, gemini-flash)
    r'_(?P<date>\d{8})'                    # date YYYYMMDD
    r'_(?P<time>\d{6})'                    # time HHMMSS
    r'(?P<suffix>.*)'                      # everything after
    r'$'
)

# Phase patterns in the suffix
PHASE_RE = re.compile(r'_(?P<phase>p2b|p3b|p4b_r\d+|p5)_')


def parse_run_folder(folder_name: str) -> dict:
    """Parse a run folder name into its components."""
    m = RUN_FOLDER_RE.match(folder_name)
    if not m:
        return {
            "model": "unknown",
            "timestamp": "",
            "phase": "unknown",
            "task_type": "unknown",
        }

    model = m.group("model")
    date = m.group("date")
    time_ = m.group("time")
    suffix = m.group("suffix")
    timestamp = f"{date}_{time_}"

    # Determine task type from suffix
    if "function-tasks" in suffix:
        task_type = "function-tasks"
    elif "real-tasks" in suffix:
        task_type = "real-tasks"
    else:
        task_type = None  # Will be inferred later

    # Determine phase from suffix
    phase_m = PHASE_RE.search(suffix)
    if phase_m:
        phase = phase_m.group("phase")
    else:
        phase = None  # Will be inferred later

    return {
        "model": model,
        "timestamp": timestamp,
        "phase": phase,
        "task_type": task_type,
        "suffix": suffix,
    }


def infer_task_type_from_data(data: dict) -> str:
    """Infer task type from the results data (task IDs)."""
    tasks = data.get("tasks", [])
    if not tasks:
        return "unknown"

    # Function tasks use numeric IDs (task_1, task_2, ...)
    # Real tasks use difficulty-prefixed IDs (task_e1, task_m1, task_h1, ...)
    task_ids = [t.get("task_id", "") for t in tasks]
    has_difficulty_prefix = any(
        re.match(r'^task_[emh]\d+', tid) for tid in task_ids
    )
    has_numeric_only = any(
        re.match(r'^task_\d+$', tid) for tid in task_ids
    )
    # Some hardened tasks use task_h100+ style IDs
    has_hardened = any(
        re.match(r'^task_h\d{3}', tid) for tid in task_ids
    )

    if has_difficulty_prefix and not has_numeric_only:
        return "real-tasks"
    elif has_numeric_only and not has_difficulty_prefix:
        return "function-tasks"
    elif has_difficulty_prefix and has_numeric_only:
        # Mixed -- likely real-tasks with some hardened tasks
        return "real-tasks"
    else:
        return "unknown"


def infer_phase(parsed: dict, task_type: str) -> str:
    """Infer phase when not explicitly labeled in folder name.

    For older naming conventions without explicit phase labels:
    - function-tasks_parallel -> likely p2b (function task eval)
    - real-tasks_parallel or just parallel -> likely p3b (real task eval)
    But without explicit labels, we mark as 'pre-pipeline' since we can't
    definitively determine if it was p2b vs p5, or p3b vs p4b, etc.
    """
    if parsed.get("phase"):
        return parsed["phase"]

    suffix = parsed.get("suffix", "")

    # Old naming: function-tasks without phase label
    if "function-tasks" in suffix:
        return "pre-pipeline-func"

    # Old naming: real-tasks or just parallel without phase label
    if "real-tasks" in suffix:
        return "pre-pipeline-real"

    # Just "_parallel" -- need to infer from task type
    if task_type == "function-tasks":
        return "pre-pipeline-func"
    elif task_type == "real-tasks":
        return "pre-pipeline-real"

    return "pre-pipeline-real"  # default: most bare "_parallel" runs are real-tasks


def check_rate_limit_issues(data: dict) -> bool:
    """Check if a run likely had rate limit issues.

    Criteria: pass_rate == 0 AND total_tasks > 0.
    """
    total = data.get("total", 0)
    passed = data.get("passed", 0)
    return total > 0 and passed == 0


def build_inventory():
    """Walk all results.json files and build the inventory."""
    rows = []

    if not S3_RESULTS_DIR.exists():
        print(f"ERROR: {S3_RESULTS_DIR} does not exist")
        sys.exit(1)

    # Walk app directories
    for app_dir in sorted(S3_RESULTS_DIR.iterdir()):
        if not app_dir.is_dir():
            continue

        app_name = app_dir.name

        # Walk run folders
        for run_dir in sorted(app_dir.iterdir()):
            if not run_dir.is_dir():
                continue

            run_folder = run_dir.name

            # Find the best results.json:
            # Prefer top-level results.json; fall back to merged/results.json
            results_path = run_dir / "results.json"
            if not results_path.exists():
                results_path = run_dir / "merged" / "results.json"
            if not results_path.exists():
                # Try any subdirectory
                candidates = list(run_dir.glob("*/results.json"))
                if candidates:
                    results_path = candidates[0]
                else:
                    continue  # No results.json found

            try:
                with open(results_path) as f:
                    data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"  WARNING: Could not read {results_path}: {e}", file=sys.stderr)
                continue

            # Parse run folder name
            parsed = parse_run_folder(run_folder)

            # Extract fields from JSON
            model = data.get("model", parsed["model"])
            total_tasks = data.get("total", 0)
            passed_tasks = data.get("passed", 0)
            pass_rate = data.get("pass_rate", 0.0)
            timestamp = data.get("timestamp", parsed["timestamp"])

            # Determine task type
            task_type = parsed.get("task_type")
            if not task_type:
                task_type = infer_task_type_from_data(data)

            # Determine phase
            phase = infer_phase(parsed, task_type)

            # Check for audit_summary.md in the run folder
            has_audit = (run_dir / "audit_summary.md").exists()

            # Check for rate limit issues
            has_rate_limit = check_rate_limit_issues(data)

            rows.append({
                "app": app_name,
                "run_folder": run_folder,
                "model": model,
                "phase": phase,
                "task_type": task_type,
                "total_tasks": total_tasks,
                "passed_tasks": passed_tasks,
                "pass_rate": pass_rate,
                "timestamp": timestamp,
                "has_audit_summary": has_audit,
                "has_rate_limit_issues": has_rate_limit,
            })

    return rows


def write_csv(rows: list):
    """Write inventory to CSV."""
    fieldnames = [
        "app", "run_folder", "model", "phase", "task_type",
        "total_tasks", "passed_tasks", "pass_rate", "timestamp",
        "has_audit_summary", "has_rate_limit_issues",
    ]

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nCSV written to: {OUTPUT_CSV}")
    print(f"Total rows: {len(rows)}")


def print_summary(rows: list):
    """Print a summary table grouped by app showing phase progression."""

    # Phase display order
    phase_order = [
        "p2b", "p3b", "p4b_r1", "p4b_r2", "p4b_r3", "p5",
        "pre-pipeline-func", "pre-pipeline-real",
    ]
    phase_labels = {
        "p2b": "P2b (Func Eval)",
        "p3b": "P3b (Real Eval)",
        "p4b_r1": "P4b R1 (Harden)",
        "p4b_r2": "P4b R2 (Harden)",
        "p4b_r3": "P4b R3 (Harden)",
        "p5": "P5 (Final)",
        "pre-pipeline-func": "Pre-Pipe Func",
        "pre-pipeline-real": "Pre-Pipe Real",
    }

    # Group by app
    apps = defaultdict(list)
    for row in rows:
        apps[row["app"]].append(row)

    # Print per-app summary
    print("\n" + "=" * 120)
    print("PHASE INVENTORY SUMMARY")
    print("=" * 120)

    for app_name in sorted(apps.keys()):
        app_rows = apps[app_name]

        # Group by model
        models = defaultdict(list)
        for r in app_rows:
            models[r["model"]].append(r)

        print(f"\n{'─' * 120}")
        print(f"APP: {app_name} ({len(app_rows)} runs)")
        print(f"{'─' * 120}")

        for model_name in sorted(models.keys()):
            model_rows = models[model_name]

            # Group by phase
            phases = defaultdict(list)
            for r in model_rows:
                phases[r["phase"]].append(r)

            print(f"\n  Model: {model_name}")
            print(f"  {'Phase':<22} {'Task Type':<18} {'Runs':>5} {'Best Pass Rate':>15} {'Last Pass Rate':>16} {'Rate Lim':>9}")
            print(f"  {'─' * 22} {'─' * 18} {'─' * 5} {'─' * 15} {'─' * 16} {'─' * 9}")

            for phase in phase_order:
                if phase not in phases:
                    continue
                phase_runs = phases[phase]

                # Determine task types in this phase
                task_types = set(r["task_type"] for r in phase_runs)
                for tt in sorted(task_types):
                    tt_runs = [r for r in phase_runs if r["task_type"] == tt]
                    # Sort by timestamp
                    tt_runs.sort(key=lambda r: r["timestamp"])

                    best_rate = max(r["pass_rate"] for r in tt_runs)
                    last_rate = tt_runs[-1]["pass_rate"]
                    num_runs = len(tt_runs)
                    rate_lim_count = sum(1 for r in tt_runs if r["has_rate_limit_issues"])
                    rate_lim_str = f"{rate_lim_count}/{num_runs}" if rate_lim_count > 0 else ""

                    label = phase_labels.get(phase, phase)
                    print(f"  {label:<22} {tt:<18} {num_runs:>5} {best_rate:>14.1f}% {last_rate:>15.1f}% {rate_lim_str:>9}")

    # Overall stats
    print(f"\n{'=' * 120}")
    print("OVERALL STATISTICS")
    print(f"{'=' * 120}")

    total_runs = len(rows)
    total_apps = len(apps)
    rate_limited = sum(1 for r in rows if r["has_rate_limit_issues"])
    audited = sum(1 for r in rows if r["has_audit_summary"])

    models_set = set(r["model"] for r in rows)
    phases_set = set(r["phase"] for r in rows)

    print(f"  Total apps:          {total_apps}")
    print(f"  Total runs:          {total_runs}")
    print(f"  Models:              {', '.join(sorted(models_set))}")
    print(f"  Phases present:      {', '.join(sorted(phases_set))}")
    print(f"  Runs with audit:     {audited}")
    print(f"  Rate-limited runs:   {rate_limited}")

    # Per-model summary
    print(f"\n  {'Model':<16} {'Runs':>6} {'Avg Pass Rate':>14} {'Rate-Limited':>13}")
    print(f"  {'─' * 16} {'─' * 6} {'─' * 14} {'─' * 13}")
    for model_name in sorted(models_set):
        m_rows = [r for r in rows if r["model"] == model_name]
        avg_rate = sum(r["pass_rate"] for r in m_rows) / len(m_rows) if m_rows else 0
        rl = sum(1 for r in m_rows if r["has_rate_limit_issues"])
        print(f"  {model_name:<16} {len(m_rows):>6} {avg_rate:>13.1f}% {rl:>13}")

    # Per-phase summary (across all apps/models)
    print(f"\n  {'Phase':<22} {'Runs':>6} {'Avg Pass Rate':>14} {'Rate-Limited':>13}")
    print(f"  {'─' * 22} {'─' * 6} {'─' * 14} {'─' * 13}")
    for phase in phase_order:
        p_rows = [r for r in rows if r["phase"] == phase]
        if not p_rows:
            continue
        avg_rate = sum(r["pass_rate"] for r in p_rows) / len(p_rows) if p_rows else 0
        rl = sum(1 for r in p_rows if r["has_rate_limit_issues"])
        label = phase_labels.get(phase, phase)
        print(f"  {label:<22} {len(p_rows):>6} {avg_rate:>13.1f}% {rl:>13}")

    # Apps that completed all phases (p2b through p5)
    print(f"\n  PIPELINE COMPLETION (apps with explicit p2b -> p5 phases):")
    required_phases = {"p2b", "p3b", "p4b_r1", "p4b_r2", "p4b_r3", "p5"}
    for app_name in sorted(apps.keys()):
        app_phases = set(r["phase"] for r in apps[app_name])
        completed = required_phases & app_phases
        missing = required_phases - app_phases
        if completed:
            status = "COMPLETE" if not missing else f"missing: {', '.join(sorted(missing))}"
            # Get p5 real-tasks pass rate if available
            p5_real = [r for r in apps[app_name] if r["phase"] == "p5" and r["task_type"] == "real-tasks"]
            p5_func = [r for r in apps[app_name] if r["phase"] == "p5" and r["task_type"] == "function-tasks"]
            p5_info = ""
            if p5_real:
                best = max(r["pass_rate"] for r in p5_real)
                p5_info += f" | P5 real: {best:.1f}%"
            if p5_func:
                best = max(r["pass_rate"] for r in p5_func)
                p5_info += f" | P5 func: {best:.1f}%"
            print(f"    {app_name:<40} {status}{p5_info}")


def main():
    print("Building phase inventory from S3 results...")
    rows = build_inventory()

    if not rows:
        print("No results found!")
        sys.exit(1)

    write_csv(rows)
    print_summary(rows)


if __name__ == "__main__":
    main()
