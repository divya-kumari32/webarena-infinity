# Docs vs No-Docs Ablation Analysis

**Generated**: 2026-03-19 21:17
**Apps analyzed**: 5
**Task filter**: real tasks only, hard tasks ≤ h60

## Dimension 1: Functional Complexity (LLM-extracted from code)

| App | With Docs | No Docs |
|-----|----------|---------|
| elation-prescriptions | 71 | 67 |
| figma-slides | 117 | 91 |
| gmail-accounts-and-contacts | 69 | 52 |
| xero-invoicing | 96 | 64 |
| gitlab-plan-and-track | 79 | 83 |

## Dimension 2: Task Diversity (Real Tasks)

| App | | Count | Mean Pairwise | 5-NN Dist | Optimal K | Cluster Entropy | Silhouette |
|-----|---|-------|--------------|----------|----------|----------------|-----------|
| elation-prescriptions | Docs | 100 | 0.3105 | 0.2099 | 13 | 3.55 | 0.185 |
|  | NoDocs | 100 | 0.2908 | 0.1995 | 5 | 2.01 | 0.133 |
| figma-slides | Docs | 100 | 0.3946 | 0.2832 | 12 | 3.45 | 0.139 |
|  | NoDocs | 100 | 0.3670 | 0.2434 | 4 | 1.82 | 0.165 |
| gmail-accounts-and-contacts | Docs | 100 | 0.3836 | 0.2572 | 2 | 0.93 | 0.190 |
|  | NoDocs | 80 | 0.3793 | 0.2668 | 2 | 0.95 | 0.182 |
| xero-invoicing | Docs | 100 | 0.3769 | 0.2553 | 14 | 3.73 | 0.199 |
|  | NoDocs | 100 | 0.3500 | 0.2213 | 6 | 2.53 | 0.226 |
| gitlab-plan-and-track | Docs | 100 | 0.3779 | 0.2821 | 15 | 3.81 | 0.107 |
|  | NoDocs | 100 | 0.3762 | 0.2812 | 14 | 3.67 | 0.101 |

## Dimension 3: Seed Data Richness

| App | | data.js LOC | Entities | Unique Fields | Unique Strings |
|-----|---|------------|----------|--------------|----------------|
| elation-prescriptions | Docs | 800 | 315 | 139 | 466 |
| | NoDocs | 965 | 371 | 126 | 626 |
| figma-slides | Docs | 1343 | 298 | 188 | 402 |
| | NoDocs | 930 | 453 | 535 | 643 |
| gmail-accounts-and-contacts | Docs | 682 | 130 | 182 | 169 |
| | NoDocs | 372 | 194 | 164 | 355 |
| xero-invoicing | Docs | 398 | 292 | 135 | 451 |
| | NoDocs | 322 | 108 | 106 | 380 |
| gitlab-plan-and-track | Docs | 297 | 194 | 152 | 347 |
| | NoDocs | 463 | 285 | 221 | 684 |

## Dimension 4: Verifier Complexity

| App | | Mean LOC | Mean Assertions | Mean State Depth | % With Loops |
|-----|---|---------|----------------|-----------------|-------------|
| elation-prescriptions | Docs | 42.6 | 11.8 | 0.1 | 91% |
| | NoDocs | 34.7 | 13.8 | 0.7 | 82% |
| figma-slides | Docs | 40.7 | 12.8 | 0.1 | 92% |
| | NoDocs | 37.6 | 8.8 | 0.5 | 100% |
| gmail-accounts-and-contacts | Docs | 35.5 | 8.5 | 0.1 | 85% |
| | NoDocs | 49.0 | 11.9 | 0.3 | 94% |
| xero-invoicing | Docs | 31.3 | 10.1 | 0.1 | 92% |
| | NoDocs | 42.1 | 13.6 | 0.4 | 85% |
| gitlab-plan-and-track | Docs | 45.4 | 15.1 | 0.6 | 100% |
| | NoDocs | 24.0 | 11.1 | 1.0 | 99% |

## Dimension 5: Task Specificity & Difficulty Calibration

| App | | Count | Mean Words | Entity Ref % | Easy | Medium | Hard |
|-----|---|-------|-----------|-------------|------|--------|------|
| elation-prescriptions | Docs | 100 | 22.5 | 41% | 6.3 | 14.9 | 30.5 |
| | NoDocs | 100 | 23.8 | 80% | 7.2 | 13.5 | 32.8 |
| figma-slides | Docs | 100 | 20.0 | 54% | 7.3 | 14.4 | 26.1 |
| | NoDocs | 100 | 15.5 | 70% | 8.4 | 13.4 | 18.5 |
| gmail-accounts-and-contacts | Docs | 100 | 15.8 | 51% | 4.8 | 11.1 | 21.0 |
| | NoDocs | 80 | 19.2 | 75% | 7.4 | 15.4 | 27.1 |
| xero-invoicing | Docs | 100 | 14.2 | 76% | 7.3 | 10.7 | 17.7 |
| | NoDocs | 100 | 21.4 | 84% | 9.2 | 16.9 | 26.9 |
| gitlab-plan-and-track | Docs | 100 | 18.5 | 63% | 8.9 | 15.3 | 22.8 |
| | NoDocs | 100 | 18.8 | 69% | 8.7 | 18.1 | 22.4 |

## Dimension 6: Authenticity (Feature Precision/Recall vs Docs)

| App | | Precision | Recall | F1 | Feature Count |
|-----|---|----------|--------|-----|--------------|
| elation-prescriptions | Docs | 0.846 | 0.641 | 0.729 | 123 |
| | NoDocs | 0.570 | 0.481 | 0.522 | 107 |
| figma-slides | Docs | 0.587 | 0.410 | 0.483 | 264 |
| | NoDocs | 0.488 | 0.284 | 0.359 | 168 |
| gmail-accounts-and-contacts | Docs | 0.190 | 0.215 | 0.202 | 147 |
| | NoDocs | 0.154 | 0.127 | 0.139 | 130 |
| xero-invoicing | Docs | 0.789 | 0.496 | 0.609 | 209 |
| | NoDocs | 0.830 | 0.475 | 0.604 | 147 |
| gitlab-plan-and-track | Docs | 0.866 | 0.321 | 0.468 | 216 |
| | NoDocs | 0.827 | 0.303 | 0.443 | 191 |
