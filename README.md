<p align="center">
  <img src="bench/output/trajectory_collage.gif" alt="Browser agents navigating generated environments" width="800">
</p>

<h1 align="center">WebArena-Infinity</h1>
<h3 align="center">Generating Browser Environments with Verifiable Tasks at Scale</h3>

<p align="center">
  <a href="https://web-arena-x.github.io/webarena-infinity/"><img src="https://img.shields.io/badge/Blog_Post-blue?style=flat&logo=googlechrome&logoColor=white" alt="Blog Post"></a>
  <a href="http://35.168.80.130/"><img src="https://img.shields.io/badge/Environment_Hub-green?style=flat&logo=globe&logoColor=white" alt="Environment Hub"></a>
  <a href="https://huggingface.co/datasets/webarena-x/webarena-infinity-trajectories"><img src="https://img.shields.io/badge/Dataset-yellow?style=flat&logo=huggingface&logoColor=white" alt="Dataset"></a>
  <a href="https://github.com/web-arena-x/webarena-infinity"><img src="https://img.shields.io/badge/GitHub-black?style=flat&logo=github&logoColor=white" alt="GitHub"></a>
</p>

WebArena-Infinity is a scalable approach for automatically generating realistic web environments paired with verifiable tasks, enabling robust training and evaluation of general-purpose browser agents. Instead of relying on labor-intensive manual construction, our approach uses a multi-agent system that coordinates coding agents with privileged access to environment internals and browser agents that interact through the UI—to iteratively generate, test, audit, and refine environments. Starting from real-world artifacts such as product manuals and workflows, the approach produces high-fidelity applications, difficulty-graded tasks, and reliable programmatic verifiers, all optimized for future reinforcement learning. The result is a cost-efficient, reproducible, and extensible benchmark suite that captures meaningful real-world complexity while remaining fully automated.

## Quick Start: Explore Existing Environments

The repo ships with pre-built environments you can browse and evaluate agents against immediately.

### 1. Install

Requires Python 3.12+ and [`uv`](https://docs.astral.sh/uv/getting-started/installation/).

```bash
git clone https://github.com/web-arena-x/webarena-infinity.git
cd webarena-infinity
bash setup.sh
```

### 2. Browse an Environment

Pick any app and launch its server:

```bash
cd apps/gmail && python3 server.py --port 8000
```

Open `http://localhost:8000` in your browser to explore the app. Each environment is a self-contained web app with realistic seed data and UI interactions.

### 3. Run an Agent Against It

Set up at least one API key in a `.env` file (gitignored by default):

```bash
# .env — at least one key required
export GOOGLE_API_KEY='...'       # For gemini-flash, gemini-pro, gemini-cu
export OPENAI_API_KEY='...'       # For gpt
export ANTHROPIC_API_KEY='...'    # For claude, claude-cu
```

Then run an evaluation:

```bash
source .env

python evaluation/run_eval_parallel.py \
    --model gpt \
    --difficulty easy \
    --workers 4 \
    --web-app apps/gmail
```

Results go to `apps/<app>/results/` and include a browsable `report.html`.

### Supported Agents

| `--model` flag | Agent | API key required |
|---|---|---|
| `gpt` | GPT-4o via browser-use | `OPENAI_API_KEY` |
| `claude` | Claude Sonnet 4.6 via browser-use | `ANTHROPIC_API_KEY` |
| `gemini-flash` | Gemini Flash 3 via browser-use | `GOOGLE_API_KEY` |
| `gemini-pro` | Gemini Pro 3 via browser-use | `GOOGLE_API_KEY` |
| `gemini-cu` | Gemini computer-use (coordinate-based) | `GOOGLE_API_KEY` |
| `claude-cu` | Claude computer-use (coordinate-based) | `ANTHROPIC_API_KEY` |
| `kimi` | Moonshot Kimi K2.5 | `KIMI_API_KEY` |
| `qwen` | Alibaba Qwen 3.5 VL | `DASHSCOPE_API_KEY` |


## Quick Try: Run the Full Approach Locally

> **Warning:** The pipeline invokes Claude Code with `--dangerously-skip-permissions` so it can generate and modify code autonomously, hence there is inherent risk of unwanted behaviors. Run this in a sandboxed environment (VM, container, or disposable instance) if possible.

The full pipeline uses Claude Code to generate apps from documentation, then evaluates and iterates. This requires the [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code/overview).

### 1. Write an app description
Create a markdown file in `apps/app-description/` describing the web app you want to create for your browser-use agent. See the existing descriptions for reference:

### 2. Run the pipeline

```bash
python infra/pipeline.py \
    --app-name my-app \
    --docs-path apps/app-description/my-app.md \
    --model gemini-flash \
    --workers 4
```
This will create `apps/my-app/` with the generated web app, tasks, and the verifiers.


## AWS Setup (Parallel Multi-Environment)
For generating multiple environments in parallel on EC2, each environment gets its own instance. This section walks through the full setup.

### Prerequisites

- [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) configured with credentials (`aws configure`)
- An EC2 key pair in your target region
- A GitHub personal access token with repo access
- Claude Code CLI authentication (for the base AMI)

### 1. Configure Infrastructure

All AWS resource names and defaults are centralized in [`infra/config.sh`](infra/config.sh). Every infrastructure script sources this file. Edit it once to customize for your AWS account:

```bash
# infra/config.sh — edit these values for your setup
MM_REGION="${AWS_REGION:-us-east-1}"              # AWS region
MM_S3_BUCKET="${MM_S3_BUCKET:-mirror-mirror-results}"  # S3 bucket for results
MM_IAM_ROLE="${MM_IAM_ROLE:-mirror-mirror-ec2}"        # IAM role for EC2 instances
MM_SECURITY_GROUP="${MM_SECURITY_GROUP:-mm-pipeline}"  # Security group name
MM_INSTANCE_TYPE="${MM_INSTANCE_TYPE:-m5.4xlarge}"      # EC2 instance type
MM_PROJECT_TAG="${MM_PROJECT_TAG:-mirror-mirror}"       # AWS tag for resource discovery
```

Each value can also be overridden via environment variable without editing the file.

### 2. Environment Variables

Create a `.env` file in the repo root with your credentials:

```bash
#  Required 
export GITHUB_TOKEN='ghp_...'          # GitHub PAT for git clone/push on instances
export GITHUB_REPO='your-org/webarena-infinity'  # GitHub owner/repo
export KEY_PAIR_NAME='my-key-pair'     # Name of your EC2 key pair

#  Agent API keys (at least one) 
export GOOGLE_API_KEY='...'            # For Gemini agents
export OPENAI_API_KEY='...'            # For GPT agent
export ANTHROPIC_API_KEY='...'         # For Claude agents
```

### 3. Create a Base AMI

A base AMI pre-installs all dependencies (Python, Node.js, Claude CLI, Playwright, Chromium) so instances start fast. **This step requires manual SSH intervention** to authenticate Claude Code.

```bash
bash infra/setup/create_base_ami.sh --key-pair my-key-pair
```

The script will:
1. Launch a temporary EC2 instance
2. Install all system and Python dependencies
3. **Pause and ask you to SSH in** to run:
   ```bash
   claude login
   claude plugins install frontend-design
   ```
4. Create an AMI from the instance
5. Clean up the temporary instance

Note the AMI ID from the output — you'll use it in the next step.

### 4. Define Your Environment Manifest

Create a JSONL file where each line maps an environment to its source documentation:

```jsonl
{"env_id": "linear-account-settings", "docs_path": "apps/user-manuals/linear/02-account"}
{"env_id": "gmail-organize-and-manage", "docs_path": "apps/user-manuals/gmail/organize-and-manage"}
```

Pre-built manifests are available:
- `infra/env_manifest.jsonl` — full suite (19 environments)
- `infra/env_manifest_quick.jsonl` — quick test (2 environments)

### 5. Run

```bash
source .env

bash infra/setup/run_batches.sh \
    --manifest infra/env_manifest.jsonl \
    --batch-size 5 \
    --ami ami-0abc123def456 \
    --model gemini-flash \
    --workers 8
```

`run_batches.sh` handles the full lifecycle automatically:
1. Launches a batch of EC2 instances (one per environment)
2. Starts the pipeline on each instance
3. Polls for completion
4. Tears down finished instances
5. Launches the next batch until all environments are done

Crashed instances are kept alive for debugging. Once investigated, clean them up with:

```bash
bash infra/setup/teardown.sh --all
```

You can monitor progress while batches run:

```bash
bash infra/setup/monitor.sh --watch 120   # refresh every 2 minutes
```

### 6. Collect Results (Optional)

To aggregate results across environments into S3 with a browsable HTML dashboard, first create the bucket:

```bash
bash infra/setup/setup_s3.sh
```

Then collect:

```bash
python infra/collect_results.py
```

This generates a cross-environment summary and uploads an HTML dashboard to `http://{MM_S3_BUCKET}.s3-website-{MM_REGION}.amazonaws.com/`.

## Citation

```bibtex
@article{zhou2026wainf,
  title   = "WebArena-Infinity: Generating Browser Environments with Verifiable Tasks at Scale",
  author  = "Shuyan Zhou",
  journal = "shuyanzhou.com",
  year    = "2026",
  month   = "March",
  url     = "https://webarena.dev/webarena-infinity/"
}
```