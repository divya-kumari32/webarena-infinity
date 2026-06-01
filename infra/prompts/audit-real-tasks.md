Audit the agent evaluation results following the guide at `./docs/real-task-audit.md.`

**Result directories to audit:**
{evaluation_result_path}

Examine each result directory above. Each contains per-task folders with history.json, result.json, and screenshots/. Investigate failed tasks to determine root cause, and also flag any tasks where the agent's self-assessment (judge verdict in result.json) disagrees with the verifier outcome — these disagreements often reveal the real issue regardless of which side says pass or fail.

**Always** write an audit summary to the most recent result directory's `audit_summary.md` documenting your findings. Include:
- Overall pass rate and task counts (across all result dirs)
- For each failed task: the root cause (verifier bug, impossible task, ambiguous instruction, or agent-side failure) and any fix applied
- A summary of agent-side failures by category (navigation failure, wrong value, false claim, timeout, etc.)