# Qwen 2 + Browser-Use — Real Tasks Results

Generated: 2026-03-19

Model: `qwen` via browser-use library (3 repetitions, best-of-N merged). Data sourced from `s3://mirror-mirror-results/`. Each row uses the latest full-suite real-tasks run for that app.

Excluded apps: `figma-slides`, `figma-text-and-typography`, `elation-patient-communication` (environment quality issues).

## Results

| App | Pass/Total | SR% | Easy | Medium | Hard | Result Folder |
|:----|:----------:|:---:|:----:|:------:|:----:|:--------------|
| elation-clinical-records | 65/120 | 54.2% | 18/20 | 13/20 | 34/80 | `qwen_20260318_190909_parallel` |
| elation-prescriptions | 50/120 | 41.7% | 16/20 | 9/20 | 25/80 | `qwen_20260318_220000_parallel` |
| gitlab-plan-and-track | 52/140 | 37.1% | 15/20 | 12/20 | 25/100 | `qwen_20260319_025419_parallel` |
| gmail | 34/60 | 56.7% | 14/20 | 13/20 | 7/20 | `qwen_20260319_061817_parallel` |
| gmail-accounts-and-contacts | 40/120 | 33.3% | 17/20 | 8/20 | 15/80 | `qwen_20260319_044441_parallel` |
| handshake-career-exploration | 101/200 | 50.5% | 19/20 | 19/20 | 63/160 | `qwen_20260319_070633_parallel` |
| linear-account-settings | 79/120 | 65.8% | 19/20 | 19/20 | 41/80 | `qwen_20260319_085558_parallel` |
| paypal-my-wallet | 100/140 | 71.4% | 18/20 | 14/20 | 68/100 | `qwen_20260319_094717_parallel` |
| superhuman-general | 31/120 | 25.8% | 10/20 | 8/20 | 13/80 | `qwen_20260319_105213_parallel` |
| xero-invoicing | 67/120 | 55.8% | 19/20 | 12/20 | 36/80 | `qwen_20260319_123310_parallel` |
| **TOTAL** | **619/1260** | **49.1%** | **165/200 (82.5%)** | **127/200 (63.5%)** | **327/860 (38.0%)** | |

## By Difficulty

| Difficulty | Pass/Total | SR% |
|:-----------|:----------:|:---:|
| Easy | 165/200 | 82.5% |
| Medium | 127/200 | 63.5% |
| Hard | 327/860 | 38.0% |

## Qwen 2 vs Gemini Flash Comparison

| App | Qwen 2 SR% | Gemini Flash SR% | Delta |
|:----|:----------:|:----------------:|:-----:|
| elation-clinical-records | 54.2% | 81.7% | -27.5pp |
| elation-prescriptions | 41.7% | 80.8% | -39.2pp |
| gitlab-plan-and-track | 37.1% | 63.6% | -26.4pp |
| gmail | 56.7% | 75.0% | -18.3pp |
| gmail-accounts-and-contacts | 33.3% | 61.7% | -28.3pp |
| handshake-career-exploration | 50.5% | 50.5% | +0.0pp |
| linear-account-settings | 65.8% | 73.3% | -7.5pp |
| paypal-my-wallet | 71.4% | 88.6% | -17.1pp |
| superhuman-general | 25.8% | 50.0% | -24.2pp |
| xero-invoicing | 55.8% | 80.8% | -25.0pp |
| **TOTAL** | **49.1%** | **69.3%** | **-20.2pp** |

### By Difficulty Comparison

| Difficulty | Qwen 2 | Gemini Flash | Delta |
|:-----------|:------:|:------------:|:-----:|
| Easy | 82.5% | 91.0% | -8.5pp |
| Medium | 63.5% | 89.0% | -25.5pp |
| Hard | 38.0% | 59.7% | -21.6pp |

## Notes

- 10 apps included (3 excluded for environment quality issues).
- No functional tasks were run for Qwen 2 — only real tasks.
- Task counts match Gemini Flash (same apps, same task suites).
- Qwen 2 ties on 1 app (handshake-career-exploration) and trails on the remaining 9.
- The largest gaps are on elation-prescriptions (-39.2pp) and gmail-accounts-and-contacts (-28.3pp).
