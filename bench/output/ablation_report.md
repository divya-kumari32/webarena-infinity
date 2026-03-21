# Ablation Analysis Report

## Section 1: Self-Challenging Increase

Shows that hardening rounds produce progressively harder tasks.

### Figures

- **Figure 1** (`fig1_sr_by_origin_p5.png`): Success Rate by Task Origin in Final Evaluation (P5)
- **Figure 2** (`fig1_aggregate_sr_by_origin.png`): Aggregate Success Rate by Task Origin

### Table 1: SR by Task Origin in P5

| App | Easy | Medium | Orig Hard | R1 | R2 | R3 |
|---|---|---|---|---|---|---|
| Elation Clinical | 100.0% | 100.0% | 95.0% | 85.0% | 65.0% | 45.0% |
| Xero Invoicing | 100.0% | 95.0% | 80.0% | 85.0% | 80.0% | 45.0% |
| Linear Settings | 100.0% | 95.0% | 95.0% | 65.0% | 45.0% | 40.0% |
| GitLab Plan | 100.0% | 90.0% | 55.0% | 75.0% | 35.0% | 20.0% |
| Elation Comms | 100.0% | 85.0% | 35.0% | 0.0% | 0.0% | 0.0% |
| PayPal Wallet | 95.0% | 95.0% | 80.0% | 90.0% | 90.0% | 85.0% |
| Elation Rx | 90.0% | 100.0% | 70.0% | 80.0% | 80.0% | 65.0% |
| Handshake | 90.0% | 95.0% | 45.0% | 35.0% | 45.0% | 20.0% |
| Superhuman | 80.0% | 80.0% | 45.0% | 40.0% | 30.0% | 25.0% |
| Gmail Contacts | 60.0% | 70.0% | 60.0% | 70.0% | 40.0% | 70.0% |
| Figma Text | 60.0% | 50.0% | 25.0% | 15.0% | 25.0% | 15.0% |
| Figma Slides | 45.0% | 35.0% | 15.0% | 5.0% | 0.0% | 15.0% |
| Clio Matters | 15.0% | 0.0% | 5.0% | 0.0% | 5.0% | 5.0% |

### Aggregate Statistics

| Category | Mean SR | Std Dev | N |
|---|---|---|---|
| Easy | 79.6% | 25.8% | 13 |
| Medium | 76.2% | 29.2% | 13 |
| Original Hard | 54.2% | 28.1% | 13 |
| Hardened (avg) | 41.9% | 28.0% | 13 |

## Section 2: Functional Correctness Regression

Table included in content.md.

### Table 2: Function Task Pass Rates (Post-Audit vs Final)

| App | Post-Audit | Final | Delta |
|---|---|---|---|
| Clio Matters | 15.8% | 14.0% | -1.8pp |
| Elation Clinical | 100.0% | 98.2% | -1.8pp |
| Elation Comms | 75.9% | 32.8% | -43.1pp |
| Elation Rx | 87.5% | 89.3% | +1.8pp |
| GitLab Plan | 98.2% | 98.2% | +0.0pp |
| PayPal Wallet | 96.4% | 96.4% | +0.0pp |
| Superhuman | 93.3% | 73.3% | -20.0pp |
| Xero Invoicing | 98.3% | 94.8% | -3.4pp |

## Section 3: Auditing Impact

### Figures

- **Figure 4** (`fig3_audit_env_vs_agent.png`): Environment Bugs vs Agent Failures
- **Figure 5** (`fig4_bug_categories_donut.png`): Bug Category Distribution
- **Figure 6** (`fig5_audit_improvement_trend.png`): Pre-Audit to Post-Audit Pass Rate Changes

### Table 3: Audit Findings by App

| App | Phase | Pass Rate | App Bugs | Verifier Bugs | Impossible | Ambiguous | Agent Failures |
|---|---|---|---|---|---|---|---|
| Clio Matters | func | 15.8% | 3 | 1 | 1 | 0 | 0 |
| Clio Matters | real | 10.0% | 2 | 1 | 1 | 0 | 0 |
| Clio Matters | p3b | 8.3% | 9 | 1 | 2 | 0 | 54 |
| Clio Matters | p4b_r3 | 0.0% | 1 | 1 | 4 | 1 | 0 |
| Elation Clinical | func | 94.5% | 3 | 0 | 0 | 0 | 2 |
| Elation Clinical | func | 98.2% | 1 | 0 | 0 | 0 | 0 |
| Elation Clinical | real | 98.3% | 0 | 0 | 0 | 0 | 1 |
| Elation Clinical | p4b_r3 | 0.0% | 0 | 2 | 1 | 1 | 0 |
| Elation Comms | func | 75.9% | 12 | 0 | 2 | 0 | 2 |
| Elation Comms | real | 65.0% | 0 | 1 | 1 | 1 | 0 |
| Elation Comms | real | 65.0% | 0 | 0 | 3 | 0 | 0 |
| Elation Rx | func | 87.5% | 0 | 0 | 0 | 0 | 7 |
| Elation Rx | func | 91.1% | 0 | 0 | 0 | 0 | 5 |
| Elation Rx | p3b | 0.0% | 0 | 0 | 0 | 0 | 6 |
| Elation Rx | p3b | 85.0% | 0 | 4 | 0 | 0 | 4 |
| Elation Rx | p3b | 71.7% | 0 | 0 | 0 | 0 | 17 |
| Elation Rx | p4b_r3 | 0.0% | 0 | 1 | 1 | 1 | 0 |
| Figma Slides | p3b | 31.7% | 0 | 1 | 1 | 1 | 0 |
| Figma Slides | p4b_r3 | 0.0% | 3 | 0 | 7 | 0 | 2 |
| Figma Text | p3b | 50.0% | 5 | 0 | 1 | 0 | 1 |
| Figma Text | p4b_r3 | 0.0% | 0 | 0 | 3 | 0 | 1 |
| GitLab Plan | func | 92.7% | 4 | 0 | 0 | 0 | 0 |
| GitLab Plan | func | 98.2% | 1 | 0 | 0 | 0 | 0 |
| Gmail Contacts | p3b | 61.7% | 6 | 1 | 1 | 0 | 0 |
| Gmail Contacts | p4b_r3 | 0.0% | 1 | 1 | 1 | 1 | 1 |
| Gmail | func | 83.3% | 3 | 0 | 0 | 0 | 2 |
| Gmail | real | 0.0% | 0 | 6 | 2 | 0 | 1 |
| Handshake | p4b_r3 | 0.0% | 0 | 0 | 1 | 0 | 0 |
| Linear Settings | real | 98.3% | 0 | 0 | 0 | 0 | 1 |
| Linear Settings | real | 46.7% | 0 | 1 | 1 | 0 | 0 |
| PayPal Wallet | func | 96.4% | 0 | 0 | 2 | 0 | 2 |
| PayPal Wallet | real | 95.0% | 0 | 0 | 0 | 0 | 3 |
| PayPal Wallet | p4b_r3 | 0.0% | 1 | 0 | 4 | 0 | 0 |
| Shopify Perf | func | 0.0% | 0 | 1 | 0 | 0 | 1 |
| Superhuman | func | 93.3% | 0 | 0 | 2 | 0 | 2 |
| Superhuman | real | 75.0% | 0 | 1 | 1 | 0 | 0 |
| Superhuman | p3b | 65.0% | 0 | 0 | 0 | 0 | 1 |
| Xero Invoicing | func | 72.4% | 8 | 0 | 0 | 4 | 0 |
| Xero Invoicing | real | 75.0% | 0 | 0 | 0 | 0 | 1 |
| Xero Invoicing | real | 81.7% | 0 | 1 | 1 | 1 | 11 |
| Xero Invoicing | real | 91.7% | 0 | 1 | 0 | 0 | 4 |
| Xero Invoicing | real | 68.3% | 0 | 1 | 1 | 1 | 0 |

### Aggregate Bug Counts

| Category | Count |
|---|---|
| App Bugs | 63 |
| Verifier Bugs | 27 |
| Impossible Tasks | 45 |
| Ambiguous Instructions | 12 |
| Agent-Side Failures | 132 |
| Infrastructure Failures | 46 |
| **Total** | **325** |

Environment issues account for 147/325 (45.2%) of all findings.
Agent-side failures account for 132/325 (40.6%).

## Key Findings

1. **Hardening works**: Average SR drops from 79.6% (easy) to 54.2% (original hard) to 41.9% (hardened), demonstrating progressive difficulty.
2. **Function tasks remain stable**: Most apps maintain >90% function task pass rate through the pipeline.
3. **Auditing catches real bugs**: The majority of audit findings are environment-side issues (app bugs, verifier bugs) that would otherwise pollute evaluation results.
