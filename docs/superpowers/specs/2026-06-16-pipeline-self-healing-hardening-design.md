# Pipeline Self-Healing Hardening — Design Spec

**Date:** 2026-06-16
**Branch:** `pipeline-hardening` (off `app_gen_v1`)
**Status:** Draft for review

## Goal

Make the existing `infra/pipeline.py` run **hands-off**: every known failure mode is
detected and handled automatically (retry / fallback / model-driven regenerate /
clean classified exit), so a run never silently crashes, hangs, or stalls waiting for
a human to decide what to do. This unblocks experiment throughput that is currently
killed by per-crash babysitting.

This is **sub-project 1 of 2**. Sub-project 2 (separate spec, designed in parallel) is
a from-scratch, multi-model robust codebase inspired by — not copied from —
webarena-infinity. This spec covers only the in-job hardening of the existing pipeline.

## Scope decisions (locked)

| Decision | Choice |
|---|---|
| What to build first | Harden existing `pipeline.py` now; new codebase is a separate later spec |
| Recovery layer | **In-job only.** No external supervisor in this plan. Always exit cleanly with a status. |
| Model fallback | **Same-model deployment fallback**, config-driven. Single endpoint per model today → fallback is dormant (collapses to retry → clean-exit). List stays configurable for BlueVela / future. |
| App validation | **Functional smoke test + headless browser load**, then **model-driven** fix on failure. |
| Disk hygiene | In-job: **detect-and-flag only, never deletes** (preserves crash-recovery backups). Plus a **separate standalone cleanup script** run deliberately outside any live run. |
| Environment | External server, ~5 concurrent jobs, **no rate quota** → backoff is light defensive insurance, not a core concern. BlueVela-specific failure modes (disk-quota nodes, enroot setup) are out of scope here. |

## Core invariant

**The pipeline never authors or patches app/task code — only the model does.**
- Validators (`app_health_gate`) only *observe*; they never edit files.
- On a detected problem, the pipeline re-invokes the **model** with the diagnostics and
  lets the model make every code edit.
- The pipeline may perform *file housekeeping* (e.g. deleting orphaned `task_h*.py`
  verifier files left by a reverted hardening round) — this is cleanup of stray files,
  not authoring/fixing app logic, and is explicitly allowed.

## Recovery action vocabulary

The orchestrator chooses exactly one action per outcome:

- `CONTINUE` — recovered / succeeded, proceed.
- `RETRY` — same deployment, exponential backoff + jitter (transient).
- `FALLBACK` — next deployment of the **same** model (dormant when only one configured).
- `REGENERATE` — re-invoke the **model** (targeted fix-prompt with diagnostics) to fix
  its own output; bounded by a retry budget.
- `SELF_CLEAN` — *(in-job: detection only; deletion is the external tool's job)*.
- `CLEAN_EXIT(code)` — terminal: write classified `STATUS.json` and exit with a distinct
  code. Never hang, never crash ambiguously.

## Error taxonomy → automatic action

| # | Failure mode | Detection | Automatic action |
|---|---|---|---|
| 1 | Model serving error (429 / 5xx / conn) | model call fails | `RETRY`×N (backoff) → `FALLBACK` → `CLEAN_EXIT(MODEL_UNAVAILABLE)` |
| 2 | Gen timeout but files present | rc≠0, files valid | `CONTINUE` (existing behavior) |
| 3 | Model returns empty / `content:null` | output empty/invalid | `FALLBACK` → `CLEAN_EXIT(GEN_EMPTY)` |
| 4 | Bad app files / `server.py` won't boot / no state | `app_health_gate` fails | `REGENERATE`×N (model fix-prompt) → `CLEAN_EXIT(APP_BROKEN)` |
| 5 | Task JSON invalid / sanity fails | sanity check | `fix-sanity` (model) → recheck → `REGENERATE`×N → `CLEAN_EXIT(TASKS_INVALID)` |
| 6 | Transient eval 0/0 (browser race) | 0 tasks + app healthy | `RETRY` (existing) → `CONTINUE` |
| 7 | Persistent eval 0/0 (broken app) | 0 tasks + health-gate fails | `REGENERATE` from Phase 1 (model) → `CLEAN_EXIT(APP_BROKEN)` |
| 8 | Eval-harness 0/0 (node/server, app fine) | 0 tasks + health-gate passes | `RETRY` full-suite → `FALLBACK` (eval deployment) → `CLEAN_EXIT(EVAL_HARNESS)` |
| 9 | Eval hang (runs to deadline, stays alive) | per-eval watchdog | force-kill process group → `CLEAN_EXIT(EVAL_HANG)` |
| 10 | Disk near-full (output volume) | `disk_guard` pre-check (read-only) | loud warning → `CLEAN_EXIT(DISK_FULL)` (no deletion) |
| 11 | Wall-limit / 48h global | `SIGALRM` (existing) | snapshot → `CLEAN_EXIT(WALL_TIMEOUT)` |
| 12 | Any uncaught exception | top-level try/except | `finalize_status(FATAL, traceback)` → clean exit |

**Out of scope (needs a supervisor — sub-project 2):** bad-node disk-quota *during
container setup*, resubmitting dead/hung jobs to fresh nodes.

## Component design

### 1. `call_model_with_fallback()` — model invocation wrapper

Two tiers:

- **Tier 1 (per-request, inside the eval LLM client):** configure `browser_use`'s
  `ChatOpenAI`/litellm client with internal retry + backoff so transient per-step
  failures are absorbed without failing the task. This is where eval-time errors mostly
  occur.
- **Tier 2 (phase-level, in `pipeline.py`):** if a whole phase still fails, wait-and-retry
  the phase, then `FALLBACK` to the next configured deployment.

**Backoff policy** (light; ~5 jobs, no quota — defensive only):

| Error | Attempts | Schedule |
|---|---|---|
| 429 / overload | ≤8 | honor `Retry-After` if present; else exp 5→10→20→40→80, cap 120s |
| 5xx | ≤4 | exp 5→10→20→40 |
| conn/timeout | ≤3 | exp 3→9→27 |

- **Full jitter** on each wait (random in `[0, computed]`) — cheap, prevents the handful
  of jobs from re-colliding.
- Exhaust deployments → `CLEAN_EXIT(MODEL_UNAVAILABLE)`.

**Config:**
```python
EVAL_DEPLOYMENTS = ["deepseek-v32-az"]    # add "deepseek-v32" to enable fallback
GEN_DEPLOYMENTS  = ["litellm/aws/glm-5"]  # add alternates if they exist
```

### 2. `app_health_gate()` — functional validation (observe-only, never edits)

Runs after **Phase 1** and after **any audit phase that modifies app code** (2b/3b/4).
Runs on a free port; the server subprocess is always killed afterward; reuses
`evaluation/server.py`'s `start_server`/`kill_port` helpers; whole gate has a timeout.

Checks, in order (fail-fast with a specific diagnostic string):
1. **Structural** — required files exist (reuse `validate_app_generation`).
2. **Server boots** — `python server.py --port <free>` binds within ≤10s; if it
   crashes/exits, capture stderr.
3. **Static serve** — `GET /` → 200.
4. **State-sync contract (server-side)** —
   `GET /api/state` → 404; synthetic `PUT /api/state {json}` → 200;
   `GET /api/state` → 200 + same json; `POST /api/reset` → 200.
5. **Headless browser load** — load `index.html` in headless Chromium, wait briefly,
   confirm the **app's own JS** pushed state (server now has non-empty state). Catches
   JS-init bugs (the silent no-push 0/0 class) that endpoint checks alone miss.

On any failure → return `(False, diagnostic)`; the orchestrator triggers `REGENERATE`
via a **model fix-prompt** (new `fix-app-health` prompt template) carrying the diagnostic.

**Diagnostics flow (how evidence reaches the model):** `diagnostic` is a structured,
size-capped string assembled from the failing check — real evidence, not "it broke":
- Boot fail → captured `server.py` stderr/traceback + exit code.
- Endpoint fail → the request (e.g. `PUT /api/state`), expected vs actual HTTP status,
  response-body snippet.
- Browser-load fail → "the app's JS did not PUT state after load" **plus captured browser
  console errors / uncaught JS exceptions** via Playwright `page.on("console")` and
  `page.on("pageerror")` (the actual JS stack trace pinpointing the init bug).

It is injected into `infra/prompts/fix-app-health.md` via the existing
`load_prompt(name, **vars)` placeholder mechanism — the same path `fix-sanity-check`
already uses (`output=output[-3000:]`). Capped to the last ~3000 chars so it never blows
the prompt. The model edits the responsible file(s); the pipeline re-runs the gate;
bounded to `REGENERATE` budget attempts.

### 3. Orchestration wrappers (Approach C: shared helpers, no `main()` rewrite)

`guarded_generation_phase()`:
```
disk_guard()                                   # read-only pre-check
for attempt in 1..GEN_BUDGET (default 3):
    result = call_model_with_fallback(phase)
    if result == MODEL_UNAVAILABLE: CLEAN_EXIT(MODEL_UNAVAILABLE)
    if phase writes/edits app code:
        ok, diag = app_health_gate()
        if not ok:
            run model fix-prompt with diag; continue
    break                                       # CONTINUE
else:
    CLEAN_EXIT(APP_BROKEN | TASKS_INVALID)
finalize_status(phase, outcome)
```

`guarded_eval_phase()`:
```
disk_guard()
result = run_eval(...)                          # tier-1 backoff inside the LLM client
if eval_watchdog_fired: kill_process_group(); CLEAN_EXIT(EVAL_HANG)
if result.total == 0:
    ok, _ = app_health_gate()
    if not ok: REGENERATE from Phase 1 (bounded) else CLEAN_EXIT(APP_BROKEN)
    else: RETRY full-suite once → still 0? FALLBACK → CLEAN_EXIT(EVAL_HARNESS)
finalize_status(phase, outcome)
```

**Top-level safety net:** the whole pipeline body runs under one `try/except`; any
uncaught exception → `finalize_status(FATAL, traceback)` → clean exit. With the existing
48h `SIGALRM`, **no path crashes ambiguously or hangs silently.**

**Retry budgets (config-driven defaults):** model serving per backoff table; `REGENERATE`
on broken app = 3; task-gen attempts = 3 (existing); eval 0-task = 1 full-suite retry
(existing).

### 4. `disk_guard()` — in-job, detection only (NEVER deletes)

- Runs at start + after each phase. Measures free space on the output volume.
- If below `MIN_FREE_GB` (default 5): loud warning + `CLEAN_EXIT(DISK_FULL)` to avoid a
  corrupt mid-write crash.
- **Never deletes anything** — preserves all SIGTERM/phase-snapshot backups used for
  crash recovery from inside the node.

### 5. `finalize_status()` — per-env status reporting

Writes `STATUS.json` (to `/output/{env}/` and `logs/{env}/`), updated after each phase
and finalized at exit:
```json
{
  "env": "...", "state": "RUNNING|SUCCESS|FAILED",
  "status_code": "SUCCESS|MODEL_UNAVAILABLE|GEN_EMPTY|APP_BROKEN|TASKS_INVALID|
                  EVAL_HARNESS|EVAL_HANG|DISK_FULL|WALL_TIMEOUT|FATAL",
  "last_phase": "...", "diagnostic": "...",
  "attempts": {"phase_1_regen": 0}, "pass_rates": {"phase_2b": 0.0},
  "started": "...", "updated": "..."
}
```
Plus a one-line human summary at the end of `pipeline.log`. Process exit code is `0` on
success and a distinct small code per failure class (so the future supervisor can act
without parsing).

**Live activity log (so the user is never lost on what's happening now).** A small
`update_activity(msg)` helper does two things on every meaningful transition:
1. appends a timestamped one-liner to a human-readable **`activity.log`**, and
2. updates a live `current_activity` field in `STATUS.json`.

It is distinct from the other two outputs: `pipeline.log` is verbose full subprocess
output; `STATUS.json` is the structured snapshot; **`activity.log` is the running
narrative** — tail-able live (`tail -f logs/{env}/activity.log`) and mirrored to
`/output/{env}/` so it survives container teardown.

Called at every meaningful transition: phase start, health-gate pass/fail (with reason),
each recovery action ("regenerating app, attempt 2/3 — reason: server.py boot error"),
retry/backoff waits, eval progress milestones (iteration, pass rate), and clean-exit.
Example:
```
14:02:11  Phase 1: generating app (glm-5)
14:09:44  Phase 1: health gate FAILED — server.py boot error (ModuleNotFoundError: foo)
14:09:45  Phase 1: regenerating (attempt 2/3) — sending boot diagnostics to model
14:15:02  Phase 1: health gate PASSED
14:15:03  Phase 2b: eval running (iter 1, 60 tasks)
14:48:20  Phase 2b: pass rate 92% (55/60)
```

### 6. Standalone cleanup script (separate file, runs OUTSIDE any live pipeline)

`infra/cleanup_results.py` (or similar):
- Prunes stale folders under `webarena-results` to relieve disk-quota pressure.
- Safety per cleanup-trap rule: **`--dry-run` default**, tar-backup before delete, verify
  non-empty, never blind `cp -r`.
- Refuses to delete an env's data if a corresponding run looks active (e.g. recent
  `STATUS.json` with `state: RUNNING` or a fresh mtime).
- Explicitly decoupled from the pipeline so crash-recovery and cleanup never collide.

## File structure

| File | Responsibility | Change |
|---|---|---|
| `infra/pipeline.py` | Orchestration + guarded wrappers + status | Modify |
| `infra/recovery.py` *(new)* | `call_model_with_fallback`, backoff, `classify_failure`, deployment config | Create |
| `infra/app_health.py` *(new)* | `app_health_gate` (boot + endpoints + browser load) | Create |
| `infra/status.py` *(new)* | `finalize_status` / `STATUS.json` schema + writer; `update_activity()` + `activity.log` (live narrative + `current_activity`) | Create |
| `infra/prompts/fix-app-health.md` *(new)* | Model fix-prompt carrying smoke-test diagnostics | Create |
| `infra/cleanup_results.py` *(new)* | Standalone, safe, out-of-band disk cleanup | Create |
| `evaluation/run_eval_parallel.py` | Tier-1 LLM-client retry/backoff config | Modify |
| `tests/...` | Unit tests per component | Create |

Rationale: each new module has one clear responsibility and is testable in isolation,
keeping `pipeline.py` an orchestrator rather than a monolith.

## Testing strategy

- **`app_health.py`** — fixtures: a known-good app dir (passes), a `server.py` that
  exits on boot (fails step 2), a server that 500s on PUT (fails step 4), an app whose JS
  never PUTs (fails step 5). Assert correct `(ok, diagnostic)`.
- **`recovery.py`** — mock a model call raising 429/5xx/conn; assert backoff schedule,
  jitter bounds, attempt counts, deployment rotation, and `MODEL_UNAVAILABLE` on exhaustion.
- **`status.py`** — assert `STATUS.json` schema, checkpoint updates, exit-code mapping;
  assert `update_activity()` appends a timestamped line to `activity.log` AND updates
  `current_activity` in `STATUS.json`; assert both are mirrored to `/output/{env}/`.
- **`cleanup_results.py`** — temp dir with stale + active-looking envs; assert dry-run
  lists correctly, tar-backup created, active env skipped, nothing deleted without confirm.
- **Orchestration** — simulate each taxonomy row; assert the expected terminal
  `status_code` / `CONTINUE`.

## Out of scope (explicit)

- External supervisor / job resubmission (sub-project 2).
- The from-scratch new codebase (sub-project 2).
- Cross-model fallback (consistency: same-model only).
- Reducing iterations / reps / tasks (quality must not drop).
- BlueVela-specific setup failures (disk-quota nodes, enroot).
