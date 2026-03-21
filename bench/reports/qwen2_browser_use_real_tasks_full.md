# Qwen 2 + Browser-Use — Real Tasks Results

Generated: 2026-03-19

Model: `qwen` via browser-use library (3 repetitions, best-of-N merged). Data sourced from `s3://mirror-mirror-results/`. Each row uses the latest full-suite real-tasks run for that app.

## Results

| App | Pass/Total | SR% | Easy | Medium | Hard | Avg Steps | Avg Time | Result Folder |
|:----|:----------:|:---:|:----:|:------:|:----:|:---------:|:--------:|:--------------|
| elation-clinical-records | 65/120 | 54.2% | 18/20 | 13/20 | 34/80 | — | — | `qwen_20260318_190909_parallel` |
| elation-patient-communication | 49/120 | 40.8% | 17/20 | 10/20 | 22/80 | — | — | `qwen_20260318_203538_parallel` |
| elation-prescriptions | 50/120 | 41.7% | 16/20 | 9/20 | 25/80 | — | — | `qwen_20260318_220000_parallel` |
| figma-slides | 10/120 | 8.3% | 5/20 | 4/20 | 1/80 | — | — | `qwen_20260318_232338_parallel` |
| figma-text-and-typography | 30/120 | 25.0% | 14/20 | 6/20 | 10/80 | — | — | `qwen_20260319_011413_parallel` |
| gitlab-plan-and-track | 52/140 | 37.1% | 15/20 | 12/20 | 25/100 | — | — | `qwen_20260319_025419_parallel` |
| gmail | 34/60 | 56.7% | 14/20 | 13/20 | 7/20 | — | — | `qwen_20260319_061817_parallel` |
| gmail-accounts-and-contacts | 40/120 | 33.3% | 17/20 | 8/20 | 15/80 | — | — | `qwen_20260319_044441_parallel` |
| handshake-career-exploration | 101/200 | 50.5% | 19/20 | 19/20 | 63/160 | — | — | `qwen_20260319_070633_parallel` |
| linear-account-settings | 79/120 | 65.8% | 19/20 | 19/20 | 41/80 | — | — | `qwen_20260319_085558_parallel` |
| paypal-my-wallet | 100/140 | 71.4% | 18/20 | 14/20 | 68/100 | — | — | `qwen_20260319_094717_parallel` |
| superhuman-general | 31/120 | 25.8% | 10/20 | 8/20 | 13/80 | — | — | `qwen_20260319_105213_parallel` |
| xero-invoicing | 67/120 | 55.8% | 19/20 | 12/20 | 36/80 | — | — | `qwen_20260319_123310_parallel` |
| **TOTAL** | **708/1620** | **43.7%** | **201/260 (77.3%)** | **147/260 (56.5%)** | **360/1100 (32.7%)** | | | |

## By Difficulty

| Difficulty | Pass/Total | SR% |
|:-----------|:----------:|:---:|
| Easy | 201/260 | 77.3% |
| Medium | 147/260 | 56.5% |
| Hard | 360/1100 | 32.7% |

## Qwen 2 vs Gemini Flash Comparison

| App | Qwen 2 SR% | Gemini Flash SR% | Delta |
|:----|:----------:|:----------------:|:-----:|
| elation-clinical-records | 54.2% | 81.7% | -27.5pp |
| elation-patient-communication | 40.8% | 36.7% | +4.2pp |
| elation-prescriptions | 41.7% | 80.8% | -39.2pp |
| figma-slides | 8.3% | 19.2% | -10.8pp |
| figma-text-and-typography | 25.0% | 31.7% | -6.7pp |
| gitlab-plan-and-track | 37.1% | 63.6% | -26.4pp |
| gmail | 56.7% | 75.0% | -18.3pp |
| gmail-accounts-and-contacts | 33.3% | 61.7% | -28.3pp |
| handshake-career-exploration | 50.5% | 50.5% | +0.0pp |
| linear-account-settings | 65.8% | 73.3% | -7.5pp |
| paypal-my-wallet | 71.4% | 88.6% | -17.1pp |
| superhuman-general | 25.8% | 50.0% | -24.2pp |
| xero-invoicing | 55.8% | 80.8% | -25.0pp |
| **TOTAL** | **43.7%** | **60.4%** | **-16.7pp** |

### By Difficulty Comparison

| Difficulty | Qwen 2 | Gemini Flash | Delta |
|:-----------|:------:|:------------:|:-----:|
| Easy | 77.3% | 85.8% | -8.5pp |
| Medium | 56.5% | 81.5% | -25.0pp |
| Hard | 32.7% | 49.4% | -16.6pp |

## Notes

- No functional tasks were run for Qwen 2 — only real tasks.
- Task counts match Gemini Flash (same apps, same task suites).
- Steps and timing data not extracted (available in per-task details within results.json).
- Qwen 2 wins on only 1 app (elation-patient-communication, +4.2pp) and ties on 1 (handshake-career-exploration). Gemini Flash leads on the remaining 11 apps.
- The largest gaps are on elation-prescriptions (-39.2pp) and gmail-accounts-and-contacts (-28.3pp).
