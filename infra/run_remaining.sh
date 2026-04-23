#!/usr/bin/env bash
# Continue from running glm5-gptoss: wait for it, then run qwen + deepseek.
set -u
cd /webarena-infinity

source ~/.profile 2>/dev/null || true
source /webarena-infinity/.venv/bin/activate 2>/dev/null || true

LOG_DIR="/webarena-infinity/logs/experiments"
GLM5_MODEL="openai:coreweave/glmv5"
GLM_PARAMS='{"extra_body":{"chat_template_kwargs":{"enable_thinking":false}}}'
DOCS="apps/user-manuals/gmail"

run_experiment() {
    local app_name="$1"
    local gen_model="$2"
    local eval_model="$3"
    local max_iter="${4:-2}"
    local model_params="${5:-}"
    local logfile="$LOG_DIR/${app_name//\//_}.log"

    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting: $app_name (gen=$gen_model, eval=$eval_model, iter=$max_iter)"
    local mp_flag=()
    if [ -n "$model_params" ]; then
        mp_flag=(--model-params "$model_params")
    fi
    python infra/pipeline.py \
        --app-name "$app_name" \
        --docs-path "$DOCS" \
        --model "$eval_model" \
        --agent deepagents \
        --generation-model "$gen_model" \
        --workers 2 \
        --repetitions 3 \
        --max-iterations "$max_iter" \
        --hardening-rounds 3 \
        --no-push \
        "${mp_flag[@]}" \
        > "$logfile" 2>&1
    local rc=$?
    if [ $rc -ne 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] FAILED: $app_name (exit=$rc) — skipping, moving to next"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Finished: $app_name (exit=$rc)"
    fi
    return 0
}

# Wait for glm5-gptoss to finish
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Waiting for glm5-gptoss pipeline to finish..."
while pgrep -f "experiments/glm5-gptoss" > /dev/null 2>&1; do
    sleep 60
done
echo "[$(date '+%Y-%m-%d %H:%M:%S')] glm5-gptoss done. Starting remaining experiments."

# Experiment 2: GLM-5 x Qwen
run_experiment "experiments/glm5-qwen"     "$GLM5_MODEL" "qwen"     1 "$GLM_PARAMS"

# Experiment 3: GLM-5 x DeepSeek
run_experiment "experiments/glm5-deepseek" "$GLM5_MODEL" "deepseek" 1 "$GLM_PARAMS"

echo "============================================================"
echo "All experiments complete at $(date)"
echo "============================================================"

echo ""
echo "=== RESULTS SUMMARY ==="
for d in apps/experiments/*/; do
    name=$(basename "$d")
    p5_dir=$(ls -dt "$d/results/"*_p5_parallel 2>/dev/null | grep -v function | head -1)
    if [ -n "$p5_dir" ]; then
        passed=$(grep -r '"passed": true' "$p5_dir"/*/result.json 2>/dev/null | wc -l)
        total=$(grep -r '"passed"' "$p5_dir"/*/result.json 2>/dev/null | wc -l)
        echo "$name: $passed/$total (Phase 5)"
    else
        latest=$(ls -dt "$d/results/"*_parallel 2>/dev/null | head -1)
        if [ -n "$latest" ]; then
            passed=$(grep -r '"passed": true' "$latest"/*/result.json 2>/dev/null | wc -l)
            total=$(grep -r '"passed"' "$latest"/*/result.json 2>/dev/null | wc -l)
            echo "$name: $passed/$total ($(basename "$latest"))"
        else
            echo "$name: no results"
        fi
    fi
done
