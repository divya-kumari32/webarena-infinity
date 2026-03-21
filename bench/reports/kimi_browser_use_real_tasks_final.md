# Kimi + Browser-Use — Real Tasks Results

Generated: 2026-03-20

Model: `kimi` via browser-use library (3 repetitions, best-of-N merged). Data sourced from `s3://mirror-mirror-results/`. Each row uses the latest full-suite real-tasks run for that app.

Excluded apps: `figma-slides`, `figma-text-and-typography`, `elation-patient-communication` (environment quality issues).

## Results

| App | Pass/Total | SR% | Easy | Medium | Hard | Result Folder |
|:----|:----------:|:---:|:----:|:------:|:----:|:--------------|
| elation-clinical-records | 60/120 | 50.0% | 18/20 | 15/20 | 27/80 | `kimi_20260318_181534_parallel` |
| elation-prescriptions | 28/120 | 23.3% | 3/20 | 6/20 | 19/80 | `kimi_20260318_212319_parallel` |
| gitlab-plan-and-track | 55/140 | 39.3% | 18/20 | 15/20 | 22/100 | `kimi_20260319_182807_parallel` |
| gmail | 42/60 | 70.0% | 16/20 | 16/20 | 10/20 | `kimi_20260319_054649_parallel` |
| gmail-accounts-and-contacts | 48/120 | 40.0% | 17/20 | 11/20 | 20/80 | `kimi_20260320_044149_parallel` |
| handshake-career-exploration | 100/200 | 50.0% | 18/20 | 16/20 | 66/160 | `kimi_20260319_063556_parallel` |
| linear-account-settings | 65/120 | 54.2% | 17/20 | 16/20 | 32/80 | `kimi_20260319_085615_parallel` |
| paypal-my-wallet | 99/140 | 70.7% | 18/20 | 16/20 | 65/100 | `kimi_20260319_201459_parallel` |
| superhuman-general | 18/120 | 15.0% | 5/20 | 6/20 | 7/80 | `kimi_20260319_213415_parallel` |
| xero-invoicing | 63/120 | 52.5% | 18/20 | 13/20 | 32/80 | `kimi_20260320_020810_parallel` |
| **TOTAL** | **578/1260** | **45.9%** | **148/200 (74.0%)** | **130/200 (65.0%)** | **300/860 (34.9%)** | |

## By Difficulty

| Difficulty | Pass/Total | SR% |
|:-----------|:----------:|:---:|
| Easy | 148/200 | 74.0% |
| Medium | 130/200 | 65.0% |
| Hard | 300/860 | 34.9% |

## Kimi vs Gemini Flash vs Qwen 2 Comparison

| App | Kimi SR% | Gemini Flash SR% | Qwen 2 SR% |
|:----|:--------:|:----------------:|:----------:|
| elation-clinical-records | 50.0% | 81.7% | 54.2% |
| elation-prescriptions | 23.3% | 80.8% | 41.7% |
| gitlab-plan-and-track | 39.3% | 63.6% | 37.1% |
| gmail | 70.0% | 75.0% | 56.7% |
| gmail-accounts-and-contacts | 40.0% | 61.7% | 33.3% |
| handshake-career-exploration | 50.0% | 50.5% | 50.5% |
| linear-account-settings | 54.2% | 73.3% | 65.8% |
| paypal-my-wallet | 70.7% | 88.6% | 71.4% |
| superhuman-general | 15.0% | 50.0% | 25.8% |
| xero-invoicing | 52.5% | 80.8% | 55.8% |
| **TOTAL** | **45.9%** | **69.3%** | **49.1%** |

### By Difficulty Comparison

| Difficulty | Kimi | Gemini Flash | Qwen 2 |
|:-----------|:----:|:------------:|:------:|
| Easy | 74.0% | 91.0% | 82.5% |
| Medium | 65.0% | 89.0% | 63.5% |
| Hard | 34.9% | 59.7% | 38.0% |

## Notes

- 10 apps included (3 excluded for environment quality issues).
- No functional tasks were run for Kimi — only real tasks.
- Task counts match Gemini Flash and Qwen 2 (same apps, same task suites).
- Kimi beats Qwen 2 on gmail (+13.3pp) and gmail-accounts-and-contacts (+6.7pp) but trails on elation-prescriptions (-18.3pp) and linear-account-settings (-11.7pp).
