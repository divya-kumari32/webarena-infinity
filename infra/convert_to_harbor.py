#!/usr/bin/env python3
"""Convert a WebArena-Infinity app to Harbor framework format.

Usage:
    python infra/convert_to_harbor.py --app apps/gmail-reproduced
    python infra/convert_to_harbor.py --app apps/gmail-glm5-gptoss --task-suite real-tasks
    python infra/convert_to_harbor.py --app apps/gmail --output-dir /tmp/harbor-gmail
"""

import argparse
import json
import shutil
import stat
import sys
from pathlib import Path

SHARED_APP_FILES = ["server.py", "index.html"]
SHARED_APP_DIRS = ["js", "css"]


def load_tasks(app_dir: Path, suite: str) -> list[dict]:
    tasks_file = app_dir / f"{suite}.json"
    if not tasks_file.exists():
        print(f"  Warning: {tasks_file} not found, skipping")
        return []
    with open(tasks_file) as f:
        return json.load(f)


def generate_task_toml(
    org: str, app_name: str, task: dict, suite: str,
) -> str:
    task_id = task["id"]
    difficulty = task.get("difficulty", "function")
    instruction = task["instruction"].replace('"', '\\"')
    harbor_name = f"{org}/{app_name}-{task_id}"
    keywords = [app_name, difficulty, "web-app"]
    if suite == "function-tasks":
        keywords.append("function-test")

    kw_str = ", ".join(f'"{k}"' for k in keywords)

    return f'''schema_version = "1.1"

[task]
name = "{harbor_name}"
description = "{instruction}"
keywords = [{kw_str}]

[agent]
timeout_sec = 300.0

[verifier]
timeout_sec = 60.0

[environment]
build_timeout_sec = 300.0
cpus = 1
memory_mb = 1024
allow_internet = false

[environment.healthcheck]
command = "curl -sf http://localhost:8080/api/state || exit 1"
interval_sec = 2.0
timeout_sec = 30.0
retries = 5
'''


def generate_test_sh() -> str:
    return '''#!/bin/bash
set -e
SERVER_URL="http://localhost:8080"

cd /app
python3 -c "
from verifier import verify
passed, msg = verify('$SERVER_URL')

import os
os.makedirs('/logs/verifier', exist_ok=True)
with open('/logs/verifier/reward.txt', 'w') as f:
    f.write('1' if passed else '0')
with open('/logs/verifier/message.txt', 'w') as f:
    f.write(msg)

print('PASSED' if passed else 'FAILED', '-', msg)
"
'''


def generate_dockerfile() -> str:
    return '''FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir requests
WORKDIR /app
COPY server.py index.html ./
COPY js/ ./js/
COPY css/ ./css/
COPY verifier.py ./
EXPOSE 8080
CMD ["python", "server.py", "--port", "8080"]
'''


def convert_task(
    app_dir: Path, output_dir: Path, task: dict, suite: str,
    org: str, app_name: str,
) -> None:
    task_id = task["id"]
    prefix = "fn_" if suite == "function-tasks" else ""
    task_dir = output_dir / f"{prefix}{task_id}"

    env_dir = task_dir / "environment"
    tests_dir = task_dir / "tests"
    env_dir.mkdir(parents=True, exist_ok=True)
    tests_dir.mkdir(parents=True, exist_ok=True)

    # task.toml
    (task_dir / "task.toml").write_text(
        generate_task_toml(org, app_name, task, suite)
    )

    # instruction.md
    (task_dir / "instruction.md").write_text(task["instruction"] + "\n")

    # tests/test.sh
    test_sh = tests_dir / "test.sh"
    test_sh.write_text(generate_test_sh())
    test_sh.chmod(test_sh.stat().st_mode | stat.S_IEXEC)

    # environment/Dockerfile
    (env_dir / "Dockerfile").write_text(generate_dockerfile())

    # Copy shared app files
    for fname in SHARED_APP_FILES:
        src = app_dir / fname
        if src.exists():
            shutil.copy2(src, env_dir / fname)

    for dname in SHARED_APP_DIRS:
        src = app_dir / dname
        if src.is_dir():
            dst = env_dir / dname
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)

    # Copy verifier script as verifier.py
    verify_path = task.get("verify", "")
    verifier_src = app_dir / verify_path
    if verifier_src.exists():
        shutil.copy2(verifier_src, env_dir / "verifier.py")
    else:
        print(f"  Warning: verifier not found: {verifier_src}")


def main():
    parser = argparse.ArgumentParser(description="Convert WebArena-Infinity app to Harbor format")
    parser.add_argument("--app", required=True, help="Path to app directory")
    parser.add_argument("--task-suite", choices=["real-tasks", "function-tasks", "both"], default="both")
    parser.add_argument("--output-dir", help="Output directory (default: {app}/harbor/)")
    parser.add_argument("--org", default="webarena-infinity", help="Harbor org name")
    args = parser.parse_args()

    app_dir = Path(args.app).resolve()
    if not app_dir.is_dir():
        print(f"Error: {app_dir} is not a directory")
        sys.exit(1)

    app_name = app_dir.name
    output_dir = Path(args.output_dir) if args.output_dir else app_dir / "harbor"

    # Validate shared files exist
    for fname in SHARED_APP_FILES:
        if not (app_dir / fname).exists():
            print(f"Error: required file {fname} not found in {app_dir}")
            sys.exit(1)

    suites = []
    if args.task_suite in ("real-tasks", "both"):
        suites.append("real-tasks")
    if args.task_suite in ("function-tasks", "both"):
        suites.append("function-tasks")

    total = 0
    for suite in suites:
        tasks = load_tasks(app_dir, suite)
        if not tasks:
            continue
        print(f"Converting {len(tasks)} tasks from {suite}...")
        for task in tasks:
            convert_task(app_dir, output_dir, task, suite, args.org, app_name)
            total += 1

    print(f"\nDone: {total} Harbor tasks written to {output_dir}")
    print(f"  Total size: ", end="")
    size = sum(f.stat().st_size for f in output_dir.rglob("*") if f.is_file())
    print(f"{size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
