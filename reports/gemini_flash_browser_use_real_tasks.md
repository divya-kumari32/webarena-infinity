# Gemini 3 Flash + Browser-Use — Real Tasks Results

Generated: 2026-03-16

Model: `gemini-3-flash-preview` via browser-use library. Data sourced from `s3://mirror-mirror-results/`. Each row uses the latest full-suite real-tasks run for that app.

## Results

| App | Pass/Total | SR% | Avg Steps | Avg Time | Result Folder |
|:----|:----------:|:---:|:---------:|:--------:|:--------------|
| elation-clinical-records | 98/120 | 81.7% | 17.1 | 146.2s | `gemini_20260308_171406_p5_parallel` |
| elation-patient-communication | 44/120 | 36.7% | 8.1 | 155.5s | `gemini_20260308_021259_parallel` |
| elation-prescriptions | 97/120 | 80.8% | 14.1 | 137.0s | `gemini_20260308_045634_p5_parallel` |
| figma-slides | 23/120 | 19.2% | 21.1 | 254.8s | `gemini_20260308_093527_p5_parallel` |
| figma-text-and-typography | 38/120 | 31.7% | 20.7 | 238.9s | `gemini_20260308_090215_p5_parallel` |
| gitlab-plan-and-track | 89/140 | 63.6% | 7.7 | 179.5s | `gemini_20260301_163233_parallel` |
| gmail-accounts-and-contacts | 74/120 | 61.7% | 17.3 | 196.1s | `gemini_20260308_124645_p5_parallel` |
| gmail | 45/60 | 75.0% | 6.2 | 149.1s | `gemini_20260226_184951_real-tasks_parallel` |
| handshake-career-exploration | 101/200 | 50.5% | 19.2 | 206.1s | `gemini_20260308_140355_p5_parallel` |
| linear-account-settings | 88/120 | 73.3% | 9.7 | 168.6s | `gemini_20260306_084059_parallel` |
| paypal-my-wallet | 124/140 | 88.6% | 10.4 | 107.8s | `gemini_20260308_123918_p5_parallel` |
| superhuman-general | 60/120 | 50.0% | 17.9 | 205.9s | `gemini_20260308_154224_p5_parallel` |
| xero-invoicing | 97/120 | 80.8% | 7.7 | 112.5s | `gemini_20260306_073311_parallel` |
| **OVERALL** | **978/1620** | **60.4%** | **14.1** | **170.3s** | |

## Notes

- Task counts vary per app (60–200) due to hardening rounds adding extra hard tasks.
- `clio-matters` excluded (not in current `apps/` directory).
- `shopify-web-performance` excluded (no real-tasks results in S3).
- Result folders with `p5` tag are Phase 5 final regression runs (full suite). Others are the latest available full-suite eval.
