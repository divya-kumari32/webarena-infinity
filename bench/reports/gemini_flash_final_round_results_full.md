# Gemini Flash — Final Round Results (Functional + Real Tasks)

Generated: 2026-03-19

Model: `gemini-3-flash-preview` via browser-use library. Data sourced from `analysis/s3_results/`. Each row uses the latest full-suite eval for that app (Phase 5 regression where available, otherwise last audited run). All counts use **best-of-N** (merged) results.

## Real Tasks

| App | Pass/Total | SR% | Easy | Medium | Hard | Result Folder |
|:----|:----------:|:---:|:----:|:------:|:----:|:--------------|
| elation-clinical-records | 98/120 | 81.7% | 20/20 | 20/20 | 58/80 | `gemini_20260308_171406_p5_parallel` |
| elation-patient-communication | 44/120 | 36.7% | 20/20 | 17/20 | 7/80 | `gemini_20260308_021259_parallel` |
| elation-prescriptions | 97/120 | 80.8% | 18/20 | 20/20 | 59/80 | `gemini_20260308_045634_p5_parallel` |
| figma-slides | 23/120 | 19.2% | 9/20 | 7/20 | 7/80 | `gemini_20260308_093527_p5_parallel` |
| figma-text-and-typography | 38/120 | 31.7% | 12/20 | 10/20 | 16/80 | `gemini_20260308_090215_p5_parallel` |
| gitlab-plan-and-track | 89/140 | 63.6% | 20/20 | 18/20 | 51/100 | `gemini_20260301_163233_parallel` |
| gmail | 45/60 | 75.0% | 19/20 | 14/20 | 12/20 | `gemini_20260226_184951_real-tasks_parallel` |
| gmail-accounts-and-contacts | 74/120 | 61.7% | 12/20 | 14/20 | 48/80 | `gemini_20260308_124645_p5_parallel` |
| handshake-career-exploration | 101/200 | 50.5% | 18/20 | 19/20 | 64/160 | `gemini_20260308_140355_p5_parallel` |
| linear-account-settings | 88/120 | 73.3% | 20/20 | 19/20 | 49/80 | `gemini_20260306_084059_parallel` |
| paypal-my-wallet | 124/140 | 88.6% | 19/20 | 19/20 | 86/100 | `gemini_20260308_123918_p5_parallel` |
| superhuman-general | 60/120 | 50.0% | 16/20 | 16/20 | 28/80 | `gemini_20260308_154224_p5_parallel` |
| xero-invoicing | 97/120 | 80.8% | 20/20 | 19/20 | 58/80 | `gemini_20260306_073311_parallel` |
| **TOTAL** | **978/1620** | **60.4%** | **223/260 (85.8%)** | **212/260 (81.5%)** | **543/1100 (49.4%)** | |

## Functional Tasks

| App | Pass/Total | SR% | Result Folder |
|:----|:----------:|:---:|:--------------|
| elation-clinical-records | 54/55 | 98.2% | `gemini_20260308_170247_function-tasks_p5_parallel` |
| elation-patient-communication | 19/58 | 32.8% | `gemini_20260308_012713_function-tasks_parallel` |
| elation-prescriptions | 50/56 | 89.3% | `gemini_20260308_043100_function-tasks_p5_parallel` |
| figma-slides | 28/61 | 45.9% | `gemini_20260308_090017_function-tasks_p5_parallel` |
| figma-text-and-typography | 36/65 | 55.4% | `gemini_20260308_082513_function-tasks_p5_parallel` |
| gitlab-plan-and-track | 54/55 | 98.2% | `gemini_20260301_163123_function-tasks_parallel` |
| gmail | 27/30 | 90.0% | `gemini_20260226_183706_function-tasks_parallel` |
| gmail-accounts-and-contacts | 52/68 | 76.5% | `gemini_20260308_122251_function-tasks_p5_parallel` |
| handshake-career-exploration | 53/55 | 96.4% | `gemini_20260308_135257_function-tasks_p5_parallel` |
| linear-account-settings | 60/60 | 100.0% | `gemini_20260306_081806_function-tasks_parallel` |
| paypal-my-wallet | 54/56 | 96.4% | `gemini_20260308_122751_function-tasks_p5_parallel` |
| superhuman-general | 44/60 | 73.3% | `gemini_20260308_151803_function-tasks_p5_parallel` |
| xero-invoicing | 55/58 | 94.8% | `gemini_20260306_071027_function-tasks_parallel` |
| **TOTAL** | **586/737** | **79.5%** | |

## Combined Summary

| App | Func SR% | Real SR% | Combined Pass/Total | Combined SR% |
|:----|:--------:|:--------:|:-------------------:|:------------:|
| elation-clinical-records | 98.2% | 81.7% | 152/175 | 86.9% |
| elation-patient-communication | 32.8% | 36.7% | 63/178 | 35.4% |
| elation-prescriptions | 89.3% | 80.8% | 147/176 | 83.5% |
| figma-slides | 45.9% | 19.2% | 51/181 | 28.2% |
| figma-text-and-typography | 55.4% | 31.7% | 74/185 | 40.0% |
| gitlab-plan-and-track | 98.2% | 63.6% | 143/195 | 73.3% |
| gmail | 90.0% | 75.0% | 72/90 | 80.0% |
| gmail-accounts-and-contacts | 76.5% | 61.7% | 126/188 | 67.0% |
| handshake-career-exploration | 96.4% | 50.5% | 154/255 | 60.4% |
| linear-account-settings | 100.0% | 73.3% | 148/180 | 82.2% |
| paypal-my-wallet | 96.4% | 88.6% | 178/196 | 90.8% |
| superhuman-general | 73.3% | 50.0% | 104/180 | 57.8% |
| xero-invoicing | 94.8% | 80.8% | 152/178 | 85.4% |
| **TOTAL** | **79.5%** | **60.4%** | **1564/2357** | **66.4%** |

## By Difficulty (Real Tasks)

| Difficulty | Pass/Total | SR% |
|:-----------|:----------:|:---:|
| Easy | 223/260 | 85.8% |
| Medium | 212/260 | 81.5% |
| Hard | 543/1100 | 49.4% |

## Best-of-N vs Run-1

| Metric | Real Tasks | Functional Tasks |
|:-------|:----------:|:----------------:|
| Best-of-N | 978/1620 (60.4%) | 586/737 (79.5%) |
| Run-1 only | 953/1620 (58.8%) | 575/737 (78.0%) |
| Retry lift | +1.6pp | +1.5pp |

## Notes

- Task counts vary per app (60–200 real tasks) due to hardening rounds adding extra hard tasks.
- `clio-matters` excluded (not in current `apps/` directory).
- `shopify-web-performance` excluded (no real-tasks results in S3).
- Result folders with `p5` tag are Phase 5 final regression runs. Others are the latest available full-suite eval for apps that stopped at Phase 3.
- The three weakest apps — figma-slides (28.2%), elation-patient-communication (35.4%), and figma-text-and-typography (40.0%) — likely reflect app/environment quality issues rather than just task difficulty.
