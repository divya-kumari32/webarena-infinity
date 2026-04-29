# Running WebArena-Infinity on BlueVela

## Overview

Run the pipeline on BlueVela using Enroot containers and LSF job scheduling.
This gives you 24+ cores and 1.5TB RAM — enough to run 10+ pipelines in parallel.

## One-time Setup

### 1. Build the container image (on VSI or local with podman)

```bash
cd webarena-infinity
podman build -t registry.example.com/team/webarena-infinity:latest \
    -f infra/bluevela/Containerfile .
podman push registry.example.com/team/webarena-infinity:latest
```

### 2. Import and bundle on BlueVela

```bash
ssh bv

# Set your shared project path
export ENROOT_SHARE_PATH=/proj/dev-pre-train
source ${ENROOT_SHARE_PATH}/enroot/scripts/blue-vela-enroot-env.sh

# Import from registry
enroot import -o webarena.sqsh docker://registry.example.com/team/webarena-infinity:latest

# Create container and bundle into .run file
enroot create -n webarena webarena.sqsh
enroot bundle -n webarena -o ${ENROOT_SHARE_PATH}/enroot/webarena.run

# Cleanup intermediate files
enroot remove -f webarena
rm webarena.sqsh
```

### 3. Verify the .run file works

```bash
${ENROOT_SHARE_PATH}/enroot/webarena.run --keep python -c "
import playwright; print('Playwright OK')
from browser_use import Agent; print('browser-use OK')
"
```

## Running Pipelines

### Single pipeline

Edit `APPS` array in `run-webarena-pipeline.bsub`:

```bash
APPS=(
    "experiments/glm5-spotify|apps/app-description/spotify-music.md"
)
```

Submit:

```bash
mkdir -p logs
bsub < infra/bluevela/run-webarena-pipeline.bsub
```

### Multiple pipelines in parallel

```bash
APPS=(
    "experiments/glm5-spotify|apps/app-description/spotify-music.md"
    "experiments/glm5-gmail|apps/app-description/gmail.md"
    "experiments/glm5-linear|apps/app-description/linear.md"
    "experiments/glm5-figma|apps/app-description/figma.md"
)
```

With 8 workers per pipeline and 4 pipelines, peak memory is ~32 Chromium instances × 1.5GB ≈ 48GB (well within 1.5TB).

### Monitor

```bash
bjobs -l <JOB_ID>
tail -f /opt/nvme/$USER/webarena-logs/<JOB_ID>/pipeline_*.log
```

### Results

Results are copied to shared storage at job completion:

```
/proj/dev-pre-train/webarena-results/<JOB_ID>/
```

## Configuration

| Parameter | Default | Notes |
|-----------|---------|-------|
| GENERATION_MODEL | openai:coreweave/glmv5 | GLM-5 for app generation |
| EVAL_MODEL | deepseek | Browser agent evaluator |
| WORKERS | 8 | Chromium instances per pipeline |
| REPETITIONS | 3 | Eval repetitions per task |
| MAX_ITERATIONS | 2 | Eval-audit iterations |
| HARDENING_ROUNDS | 1 | Task hardening rounds |
| -W (wall time) | 720 min | 12 hours max |

## Updating the repo

The bsub script does `git pull` inside the container at launch. To update:
- Push changes to the GitHub repo
- Re-run the job — it picks up latest code automatically

To rebuild the container image (e.g., new Python deps):
- Rebuild and push from VSI
- Re-import and bundle on BlueVela

## Key Differences from Docker Setup

| Docker (Mac) | BlueVela (Enroot) |
|---|---|
| `docker exec webarena ...` | `enroot start ${CONTAINER_NAME} ...` |
| 2 CPUs / 8GB | 24 cores / 1.5TB |
| 4 workers max | 8-16 workers per pipeline |
| 1 pipeline | Multiple in parallel |
| Interactive monitoring | Batch logs |
| Persistent container | Job-scoped lifecycle |
