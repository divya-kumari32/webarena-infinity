#!/usr/bin/env bash
# WebArena-Infinity Batch Orchestrator for BlueVela (LSF + Enroot)
#
# Reads a JSONL manifest, generates per-env bsub scripts, submits in batches,
# polls for completion, and reports results.
#
# Usage:
#   bash infra/bluevela/run_batches_bv.sh --manifest infra/bluevela/env_manifest_bv.jsonl
#   bash infra/bluevela/run_batches_bv.sh --manifest manifest.jsonl --batch-size 2 --dry-run
#
# Requires: jq, bsub/bjobs (LSF), LITELLM_API_KEY in environment

set -euo pipefail

# ── Defaults ─────────────────────────────────────────────────────────────────

MANIFEST=""
BATCH_SIZE=2
GEN_MODEL="litellm/coreweave/glmv5.1"
EVAL_MODEL="deepseek"
AGENT="opencode"
WORKERS=4
POLL_INTERVAL=600
REPETITIONS=3
MAX_ITERATIONS=3
HARDENING_ROUNDS=3
DRY_RUN=false

# ── Parse arguments ──────────────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
    case "$1" in
        --manifest)          MANIFEST="$2";          shift 2 ;;
        --batch-size)        BATCH_SIZE="$2";        shift 2 ;;
        --gen-model)         GEN_MODEL="$2";         shift 2 ;;
        --eval-model)        EVAL_MODEL="$2";        shift 2 ;;
        --eval-model-id)     shift 2 ;; # deprecated, per-env eval_model in manifest
        --agent)             AGENT="$2";             shift 2 ;;
        --workers)           WORKERS="$2";           shift 2 ;;
        --poll-interval)     POLL_INTERVAL="$2";     shift 2 ;;
        --repetitions)       REPETITIONS="$2";       shift 2 ;;
        --max-iterations)    MAX_ITERATIONS="$2";    shift 2 ;;
        --hardening-rounds)  HARDENING_ROUNDS="$2";  shift 2 ;;
        --dry-run)           DRY_RUN=true;           shift ;;
        -h|--help)
            echo "Usage: bash $0 --manifest FILE [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --manifest FILE          JSONL manifest (required)"
            echo "  --batch-size N           Jobs per batch (default: 2)"
            echo "  --gen-model MODEL        Generation model (default: litellm/coreweave/glmv5.1)"
            echo "  --eval-model MODEL       Eval model name for pipeline (default: deepseek)"
            echo "  (per-env eval_model override supported in manifest JSON)"
            echo "  --agent AGENT            Agent type (default: opencode)"
            echo "  --workers N              Eval workers (default: 4)"
            echo "  --poll-interval SECS     Polling interval (default: 600)"
            echo "  --repetitions N          Eval repetitions (default: 3)"
            echo "  --max-iterations N       Audit loop iterations (default: 3)"
            echo "  --hardening-rounds N     Hardening rounds (default: 3)"
            echo "  --dry-run                Generate bsubs without submitting"
            exit 0
            ;;
        *) echo "ERROR: Unknown argument: $1"; exit 1 ;;
    esac
done

if [ -z "$MANIFEST" ]; then
    echo "ERROR: --manifest is required"
    exit 1
fi
if [ ! -f "$MANIFEST" ]; then
    echo "ERROR: Manifest not found: $MANIFEST"
    exit 1
fi

# ── Derive model short names ────────────────────────────────────────────────

model_short_name() {
    local model="$1"
    # Strip prefixes like litellm/, openai:, coreweave/
    local name="${model##*/}"
    name="${name##*:}"
    # Common mappings
    case "$name" in
        glmv5.1|glmv5.1*)       echo "glmv51" ;;
        glmv5*)                  echo "glmv5" ;;
        deepseek-v32-az)         echo "dsv32az" ;;
        deepseek-v32)            echo "dsv32" ;;
        deepseek-v3.2*)          echo "dsv32" ;;
        DeepSeek-V3.2*)          echo "dsv32az" ;;
        deepseek*)               echo "deepseek" ;;
        dsv4pro*)                echo "dsv4pro" ;;
        gpt-4o*)                 echo "gpt4o" ;;
        gpt-oss*)                echo "gptoss" ;;
        *)                       echo "$name" | tr '.' '-' | tr '[:upper:]' '[:lower:]' ;;
    esac
}

GEN_SHORT=$(model_short_name "$GEN_MODEL")
EVAL_SHORT=$(model_short_name "$EVAL_MODEL")

# ── Read manifest ───────────────────────────────────────────────────────────

ALL_ENVS=()
while IFS= read -r line; do
    [ -z "$line" ] && continue
    [[ "$line" == \#* ]] && continue
    ALL_ENVS+=("$line")
done < "$MANIFEST"

TOTAL=${#ALL_ENVS[@]}
if [ "$TOTAL" -eq 0 ]; then
    echo "ERROR: No environments in $MANIFEST"
    exit 1
fi

NUM_BATCHES=$(( (TOTAL + BATCH_SIZE - 1) / BATCH_SIZE ))

echo "==========================================="
echo "  WebArena-Infinity — BlueVela Batch Run"
echo "==========================================="
echo "  Manifest:        $MANIFEST"
echo "  Environments:    $TOTAL"
echo "  Batch size:      $BATCH_SIZE"
echo "  Batches:         $NUM_BATCHES"
echo "  Generation:      $AGENT + $GEN_MODEL ($GEN_SHORT)"
echo "  Eval (default):  $EVAL_MODEL ($EVAL_SHORT) — per-env override supported"
echo "  Workers:         $WORKERS"
echo "  Poll interval:   ${POLL_INTERVAL}s"
echo "  Dry run:         $DRY_RUN"
echo "==========================================="
echo ""

# ── Helper: generate bsub script ───────────────────────────────────────────

generate_bsub() {
    local env_id="$1"
    local docs_path="$2"
    local rerun_from="$3"
    local base_port="$4"
    local output_file="$5"
    local local_eval_model="${6:-$EVAL_MODEL}"

    local local_eval_short
    local_eval_short=$(model_short_name "$local_eval_model")
    local exp_name="${GEN_SHORT}-${local_eval_short}-${env_id}"
    local container_name="webarena-${env_id}"
    # Truncate container name to 50 chars, replace invalid chars, strip trailing dash
    container_name=$(printf '%s' "$container_name" | tr -c 'a-zA-Z0-9_.-' '-' | cut -c1-50 | sed 's/-$//')

    local app_name="experiments/${exp_name}"
    local log_dir="/u/divykum2/agentic/webarena-logs/${exp_name}"

    # Rerun-from block (restore from /output/)
    local restore_block=""
    local rerun_flag="--no-push"
    if [ -n "$rerun_from" ]; then
        rerun_flag="--rerun-from '${rerun_from}' --no-push"
        restore_block="
# ── Restore app from previous run ────────────────────────────────────────────

echo \"[\$(date)] Restoring app from previous run...\"
enroot start --root --rw --conf \$temp_enroot_config_file \${CONTAINER_NAME} bash -c \"
    mkdir -p /opt/webarena-infinity/apps/experiments &&
    cp -r /output/${exp_name}/experiments/${exp_name} /opt/webarena-infinity/apps/experiments/ &&
    echo 'Restored:' && ls /opt/webarena-infinity/apps/experiments/${exp_name}/
\"
"
    fi

    # Agent setup block
    local agent_setup=""
    if [ "$AGENT" = "opencode" ]; then
        agent_setup='
    # Install Node.js 20 (needed for opencode)
    if ! command -v node &>/dev/null; then
        curl -fsSL https://deb.nodesource.com/setup_20.x | bash - &&
        apt-get install -y --no-install-recommends nodejs &&
        rm -rf /var/lib/apt/lists/*
    fi &&
    npm install -g opencode-ai@latest &&
    opencode --version &&'
    else
        agent_setup='
    uv tool install "deepagents-cli==0.0.37" --with "langchain-openai==1.1.12" --with "openai==2.31.0" &&'
    fi

    cat > "$output_file" << BSUB_EOF
#!/bin/bash
# WebArena-Infinity Pipeline — ${env_id}
# Auto-generated by run_batches_bv.sh
# Experiment: ${exp_name}

#BSUB -J webarena-${env_id}
#BSUB -n 24
#BSUB -M 1.5T
#BSUB -hl
#BSUB -R "span[hosts=1]"
#BSUB -R "select[hname != 'p2-r11-n4' && hname != 'p2-r18-n3' && hname != 'p2-r03-n1' && hname != 'p2-r05-n2' && hname != 'p2-r27-n4' && hname != 'p2-r29-n3' && hname != 'p2-r29-n4' && hname != 'p2-r30-n1' && hname != 'p2-r31-n3' && hname != 'p2-r32-n1' && hname != 'p2-r09-n2' && hname != 'p2-r08-n2' && hname != 'p2-r07-n3']"
#BSUB -G grp_models
#BSUB -W 2880
#BSUB -o logs/webarena_${env_id}_%J.log
#BSUB -e logs/webarena_${env_id}_%J.err

. ~/.bashrc
set -e

# ── Configuration ─────────────────────────────────────────────────────────────

: "\${ENROOT_SHARE_PATH:=/u/divykum2/agentic}"

export ENROOT_DATA_PATH="/opt/nvme/\$USER/enroot-data"
export ENROOT_CACHE_PATH="/opt/nvme/\$USER/enroot-cache"
export ENROOT_RUNTIME_PATH="/tmp/user-\$(id -u)/enroot"
export ENROOT_TEMP_PATH="/tmp/tmp-\$(id -u)/enroot"
export XDG_RUNTIME_DIR="/tmp/run/user/\$(id -u)"
mkdir -p \${ENROOT_DATA_PATH} \${ENROOT_CACHE_PATH} \${ENROOT_RUNTIME_PATH} \${ENROOT_TEMP_PATH} \${XDG_RUNTIME_DIR}

CONTAINER_NAME="${container_name}"
ENROOT_SQSH="/proj/checkpoints/divykum2/agentic/enroot/webarena.sqsh"
LITELLM_URL="https://ete-litellm.ai-models.vpc.res.ibm.com/v1"
LITELLM_KEY="\${LITELLM_API_KEY:?Set LITELLM_API_KEY in ~/.bashrc or env}"

# ── Enroot config ─────────────────────────────────────────────────────────────

temp_enroot_config_file=\$(mktemp -t enroot.config.XXXXXX)
cat << EOF >> "\$temp_enroot_config_file"
environ() {
    env
}

mounts() {
    echo "/u/divykum2/agentic/webarena-results /output"
}
EOF

# ── Cleanup ───────────────────────────────────────────────────────────────────

cleanup() {
    local exit_code=\$?
    set +e
    echo "[\$(date)] Cleaning up..."
    echo "[\$(date)] Saving results from container..."
    enroot start --root --rw --conf \$temp_enroot_config_file \${CONTAINER_NAME} bash -c "
        mkdir -p /output/${exp_name}/experiments &&
        cp -r /opt/webarena-infinity/apps/experiments/${exp_name} /output/${exp_name}/experiments/ 2>/dev/null || true &&
        cp -r /opt/webarena-infinity/logs/ /output/${exp_name}/logs/ 2>/dev/null || true
    " 2>/dev/null || true
    ps -fu \$USER | grep "catatonit" | grep -v "grep" | awk '{print \$2}' | xargs -i kill -9 {} 2>/dev/null
    rm -rf "\${ENROOT_DATA_PATH}/\${CONTAINER_NAME}"
    rm -f "\$temp_enroot_config_file"
    exit \$exit_code
}
trap cleanup EXIT

# ── Setup container ───────────────────────────────────────────────────────────

echo "=========================================="
echo "WebArena-Infinity — ${env_id}"
echo "=========================================="
echo "Job ID: \${LSB_JOBID}"
echo "Host: \$(hostname)"
echo "Start time: \$(date)"
echo "Experiment: ${exp_name}"
echo "Generation: ${AGENT} + ${GEN_MODEL}"
echo "Eval model: ${EVAL_MODEL}"
echo "Workers: ${WORKERS}"
echo "Base port: ${base_port}"
echo "=========================================="

enroot remove -f \${CONTAINER_NAME} 2>/dev/null || true
echo "[\$(date)] Creating container from \${ENROOT_SQSH}..."
enroot create -n \${CONTAINER_NAME} \${ENROOT_SQSH}

echo "[\$(date)] Setting up webarena-infinity repo..."
enroot start --root --rw --conf \$temp_enroot_config_file \${CONTAINER_NAME} bash -c '
    export PATH="/root/.local/bin:/usr/local/bin:\$PATH" &&
    cd /opt/webarena-infinity &&
    git fetch origin user-manuals-test &&
    git checkout user-manuals-test &&
    git pull &&
    source .venv/bin/activate &&
    uv sync &&${agent_setup}
    echo "Setup complete"
'
${restore_block}
# ── Launch pipeline ──────────────────────────────────────────────────────────

LOG_DIR="${log_dir}"
mkdir -p \${LOG_DIR}

APP_LOG="\${LOG_DIR}/pipeline.log"

echo "[\$(date)] Launching pipeline for ${app_name}..."

enroot start --root --rw --conf \$temp_enroot_config_file \${CONTAINER_NAME} bash -c "
    source /opt/webarena-infinity/.venv/bin/activate &&
    cd /opt/webarena-infinity &&
    export PATH=\"/usr/local/bin:/root/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin:\\\$(python -m site --user-base)/bin:\\\$PATH\" &&
    export PLAYWRIGHT_BROWSERS_PATH='/root/.cache/ms-playwright' &&
    export PROXY_TARGET_URL='\${LITELLM_URL}' &&
    export PROXY_TARGET_KEY='\${LITELLM_KEY}' &&
    export OPENAI_API_KEY='\${LITELLM_KEY}' &&
    export OPENAI_BASE_URL='\${LITELLM_URL}' &&
    python infra/pipeline.py \\
        --app-name '${app_name}' \\
        --docs-path '${docs_path}' \\
        --model '${local_eval_model}' \\
        --agent '${AGENT}' \\
        --generation-model '${GEN_MODEL}' \\
        --workers ${WORKERS} \\
        --repetitions ${REPETITIONS} \\
        --max-iterations ${MAX_ITERATIONS} \\
        --hardening-rounds ${HARDENING_ROUNDS} \\
        --base-port ${base_port} \\
        ${rerun_flag}
" 2>&1 | tee "\${APP_LOG}"

echo "[\$(date)] Pipeline finished (exit code: \$?)"

# ── Copy results to shared storage ───────────────────────────────────────────

echo "[\$(date)] Copying results to /output..."
enroot start --root --rw --conf \$temp_enroot_config_file \${CONTAINER_NAME} bash -c "
    mkdir -p /output/${exp_name}/experiments &&
    cp -r /opt/webarena-infinity/apps/experiments/${exp_name} /output/${exp_name}/experiments/ 2>/dev/null || true &&
    cp -r /opt/webarena-infinity/logs/ /output/${exp_name}/logs/ 2>/dev/null || true
"

echo "=========================================="
echo "Pipeline finished at \$(date)"
echo "Results: /u/divykum2/agentic/webarena-results/${exp_name}/"
echo "Logs: \${LOG_DIR}/"
echo "=========================================="
BSUB_EOF
}

# ── Run batches ─────────────────────────────────────────────────────────────

FAILED_ENVS=()
DONE_ENVS=()

for (( batch=0; batch<NUM_BATCHES; batch++ )); do
    start=$(( batch * BATCH_SIZE ))
    end=$(( start + BATCH_SIZE ))
    if [ "$end" -gt "$TOTAL" ]; then
        end=$TOTAL
    fi
    batch_num=$(( batch + 1 ))
    batch_count=$(( end - start ))

    echo "==========================================="
    echo "=== Batch $batch_num / $NUM_BATCHES ($batch_count environments) ==="
    echo "==========================================="
    echo ""

    # Submit jobs for this batch
    declare -a BATCH_JOB_IDS=()
    declare -A JOB_ENV_MAP=()
    declare -A JOB_EXP_MAP=()

    for (( i=start; i<end; i++ )); do
        local_index=$(( i - start ))
        base_port=$(( 8001 + local_index * 100 ))

        line="${ALL_ENVS[$i]}"
        env_id=$(echo "$line" | python3 -c "import sys,json; print(json.load(sys.stdin)['env_id'])")
        docs_path=$(echo "$line" | python3 -c "import sys,json; print(json.load(sys.stdin)['docs_path'])")
        rerun_from=$(echo "$line" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('rerun_from',''))")
        env_eval_model=$(echo "$line" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('eval_model',''))")

        # Per-env eval_model overrides global default
        if [ -n "$env_eval_model" ]; then
            local_eval_model="$env_eval_model"
            local_eval_short=$(model_short_name "$env_eval_model")
        else
            local_eval_model="$EVAL_MODEL"
            local_eval_short="$EVAL_SHORT"
        fi

        exp_name="${GEN_SHORT}-${local_eval_short}-${env_id}"
        bsub_file="/tmp/webarena-batch-${env_id}.bsub"

        echo "  [$((local_index+1))/$batch_count] ${env_id} (port=${base_port}, eval=${local_eval_model}, exp=${exp_name})"
        if [ -n "$rerun_from" ]; then
            echo "           rerun_from=${rerun_from}"
        fi

        generate_bsub "$env_id" "$docs_path" "$rerun_from" "$base_port" "$bsub_file" "$local_eval_model"

        if $DRY_RUN; then
            echo "           [dry-run] Generated: $bsub_file"
            continue
        fi

        # Submit
        bsub_output=$(bsub < "$bsub_file" 2>&1) || {
            echo "           ERROR: bsub submission failed: $bsub_output"
            FAILED_ENVS+=("$env_id")
            continue
        }

        # Extract job ID from "Job <12345> is submitted..."
        job_id=$(echo "$bsub_output" | grep -oP 'Job <\K[0-9]+')
        if [ -z "$job_id" ]; then
            echo "           ERROR: Could not parse job ID from: $bsub_output"
            FAILED_ENVS+=("$env_id")
            continue
        fi

        echo "           Submitted: Job $job_id"
        BATCH_JOB_IDS+=("$job_id")
        JOB_ENV_MAP["$job_id"]="$env_id"
        JOB_EXP_MAP["$job_id"]="$exp_name"
    done

    echo ""

    if $DRY_RUN; then
        echo "  [dry-run] Skipping poll — no jobs submitted"
        echo ""
        continue
    fi

    if [ ${#BATCH_JOB_IDS[@]} -eq 0 ]; then
        echo "  No jobs to track in this batch."
        echo ""
        continue
    fi

    # Poll for completion
    echo "=== Polling batch $batch_num (every ${POLL_INTERVAL}s) ==="
    echo "  Tracking: ${BATCH_JOB_IDS[*]}"
    echo ""

    while true; do
        all_done=true
        echo "--- Poll $(date +%H:%M:%S) ---"

        for job_id in "${BATCH_JOB_IDS[@]}"; do
            env_id="${JOB_ENV_MAP[$job_id]}"
            stat=$(bjobs -noheader -o "stat" "$job_id" 2>/dev/null | tr -d ' ')

            case "$stat" in
                DONE)
                    echo "  $env_id ($job_id): DONE"
                    ;;
                EXIT)
                    echo "  $env_id ($job_id): EXIT (failed)"
                    ;;
                RUN)
                    echo "  $env_id ($job_id): RUNNING"
                    all_done=false
                    ;;
                PEND)
                    echo "  $env_id ($job_id): PENDING"
                    all_done=false
                    ;;
                UNKWN|ZOMBI)
                    echo "  $env_id ($job_id): $stat (node issue)"
                    ;;
                *)
                    echo "  $env_id ($job_id): $stat"
                    all_done=false
                    ;;
            esac
        done

        if $all_done; then
            echo ""
            break
        fi

        echo "  --- sleeping ${POLL_INTERVAL}s ---"
        echo ""
        sleep "$POLL_INTERVAL"
    done

    # Report results for this batch
    echo "=== Batch $batch_num Results ==="

    for job_id in "${BATCH_JOB_IDS[@]}"; do
        env_id="${JOB_ENV_MAP[$job_id]}"
        exp_name="${JOB_EXP_MAP[$job_id]}"
        stat=$(bjobs -noheader -o "stat" "$job_id" 2>/dev/null | tr -d ' ')
        log_dir="/u/divykum2/agentic/webarena-logs/${exp_name}"

        if [ "$stat" = "DONE" ]; then
            pass_rate=$(grep -oP "pass rate: \K[0-9.]+" "${log_dir}/pipeline.log" 2>/dev/null | tail -1)
            if [ -n "$pass_rate" ]; then
                echo "  $env_id: DONE — final pass rate: ${pass_rate}%"
            else
                echo "  $env_id: DONE — (no pass rate found in log)"
            fi
            DONE_ENVS+=("$env_id")
        else
            err_log="logs/webarena_${env_id}_${job_id}.err"
            echo "  $env_id: FAILED ($stat) — check: $err_log"
            FAILED_ENVS+=("$env_id")
        fi
    done

    # Cleanup
    unset BATCH_JOB_IDS
    unset JOB_ENV_MAP
    unset JOB_EXP_MAP

    echo ""
    if [ "$batch_num" -lt "$NUM_BATCHES" ]; then
        echo "Moving to next batch..."
        echo ""
    fi
done

# ── Final Summary ───────────────────────────────────────────────────────────

echo "==========================================="
echo "=== All $NUM_BATCHES batches processed ==="
echo "==========================================="
echo ""
echo "  Succeeded: ${#DONE_ENVS[@]}"
echo "  Failed:    ${#FAILED_ENVS[@]}"

if [ ${#DONE_ENVS[@]} -gt 0 ]; then
    echo ""
    echo "  Completed environments:"
    for env in "${DONE_ENVS[@]}"; do
        echo "    - $env"
    done
fi

if [ ${#FAILED_ENVS[@]} -gt 0 ]; then
    echo ""
    echo "  Failed environments:"
    for env in "${FAILED_ENVS[@]}"; do
        echo "    - $env"
    done
    exit 1
fi
