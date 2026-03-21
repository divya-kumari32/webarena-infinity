# Kimi + Browser-Use — Real Tasks Results

Generated: 2026-03-20

Model: `kimi` via browser-use library (3 repetitions, best-of-N merged). Data sourced from `s3://mirror-mirror-results/`. Each row uses the latest full-suite real-tasks run for that app.

## Results

| App | Pass/Total | SR% | Easy | Medium | Hard | Result Folder |
|:----|:----------:|:---:|:----:|:------:|:----:|:--------------|
| elation-clinical-records | 60/120 | 50.0% | 18/20 | 15/20 | 27/80 | `kimi_20260318_181534_parallel` |
| elation-patient-communication | 36/120 | 30.0% | 17/20 | 8/20 | 11/80 | `kimi_20260318_194429_parallel` |
| elation-prescriptions | 28/120 | 23.3% | 3/20 | 6/20 | 19/80 | `kimi_20260318_212319_parallel` |
| figma-slides | 10/120 | 8.3% | 5/20 | 4/20 | 1/80 | `kimi_20260318_231113_parallel` |
| figma-text-and-typography | 19/120 | 15.8% | 10/20 | 7/20 | 2/80 | `kimi_20260319_010808_parallel` |
| gitlab-plan-and-track | 55/140 | 39.3% | 18/20 | 15/20 | 22/100 | `kimi_20260319_182807_parallel` |
| gmail | 42/60 | 70.0% | 16/20 | 16/20 | 10/20 | `kimi_20260319_054649_parallel` |
| gmail-accounts-and-contacts | 48/120 | 40.0% | 17/20 | 11/20 | 20/80 | `kimi_20260320_044149_parallel` |
| handshake-career-exploration | 100/200 | 50.0% | 18/20 | 16/20 | 66/160 | `kimi_20260319_063556_parallel` |
| linear-account-settings | 65/120 | 54.2% | 17/20 | 16/20 | 32/80 | `kimi_20260319_085615_parallel` |
| paypal-my-wallet | 99/140 | 70.7% | 18/20 | 16/20 | 65/100 | `kimi_20260319_201459_parallel` |
| superhuman-general | 18/120 | 15.0% | 5/20 | 6/20 | 7/80 | `kimi_20260319_213415_parallel` |
| xero-invoicing | 63/120 | 52.5% | 18/20 | 13/20 | 32/80 | `kimi_20260320_020810_parallel` |
| **TOTAL** | **643/1620** | **39.7%** | **180/260 (69.2%)** | **149/260 (57.3%)** | **314/1100 (28.5%)** | |

## By Difficulty

| Difficulty | Pass/Total | SR% |
|:-----------|:----------:|:---:|
| Easy | 180/260 | 69.2% |
| Medium | 149/260 | 57.3% |
| Hard | 314/1100 | 28.5% |

## Kimi vs Gemini Flash vs Qwen 2 Comparison

| App | Kimi SR% | Gemini Flash SR% | Qwen 2 SR% |
|:----|:--------:|:----------------:|:----------:|
| elation-clinical-records | 50.0% | 81.7% | 54.2% |
| elation-patient-communication | 30.0% | 36.7% | 40.8% |
| elation-prescriptions | 23.3% | 80.8% | 41.7% |
| figma-slides | 8.3% | 19.2% | 8.3% |
| figma-text-and-typography | 15.8% | 31.7% | 25.0% |
| gitlab-plan-and-track | 39.3% | 63.6% | 37.1% |
| gmail | 70.0% | 75.0% | 56.7% |
| gmail-accounts-and-contacts | 40.0% | 61.7% | 33.3% |
| handshake-career-exploration | 50.0% | 50.5% | 50.5% |
| linear-account-settings | 54.2% | 73.3% | 65.8% |
| paypal-my-wallet | 70.7% | 88.6% | 71.4% |
| superhuman-general | 15.0% | 50.0% | 25.8% |
| xero-invoicing | 52.5% | 80.8% | 55.8% |
| **TOTAL** | **39.7%** | **60.4%** | **43.7%** |

### By Difficulty Comparison

| Difficulty | Kimi | Gemini Flash | Qwen 2 |
|:-----------|:----:|:------------:|:------:|
| Easy | 69.2% | 85.8% | 77.3% |
| Medium | 57.3% | 81.5% | 56.5% |
| Hard | 28.5% | 49.4% | 32.7% |

## Notes

- No functional tasks were run for Kimi — only real tasks.
- Task counts match Gemini Flash and Qwen 2 (same apps, same task suites).
- Kimi beats Qwen 2 on gmail (+13.3pp) and gmail-accounts-and-contacts (+6.7pp) but trails on elation-prescriptions (-18.3pp) and superhuman-general (-10.8pp).
