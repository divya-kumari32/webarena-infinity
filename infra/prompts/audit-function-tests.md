Audit the agent evaluation results inside `{evaluation_result_path}` following the guide at `docs/function-task-audit.md`

Examine the result directory. It contains per-task folders with history.json, result.json, and screenshots/. Investigate failed tasks to determine root cause, and also flag any tasks where the agent's self-assessment (judge verdict in result.json) disagrees with the verifier outcome — these disagreements often reveal the real issue regardless of which side says pass or fail.

**Always** write an audit summary to `{evaluation_result_path}/audit_summary.md` documenting your findings. Include:
- Overall pass rate and task counts
- For each failed task: the root cause (verifier bug, impossible task, ambiguous instruction, or agent-side failure) and any fix applied
- A summary of agent-side failures by category (navigation failure, wrong value, false claim, timeout, etc.)
