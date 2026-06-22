The {variant} task set for `apps/{app-name}` is INCONSISTENT: the task list in
`apps/{app-name}/{variant}-tasks.json` and the verifier files in
`apps/{app-name}/{variant}-tasks/` do not agree.

Here is exactly what is inconsistent (captured by the consistency checker):

```
{diagnostics}
```

Every task entry in `{variant}-tasks.json` has a `verify` field that points to a
verifier file (e.g. `{variant}-tasks/task_h21.py`), and every task MUST have its
verifier file present. Orphan verifier files with no matching json entry are also
not allowed.

Reconcile the two so they match exactly. Strongly PREFER generating the missing
verifier files over deleting tasks — the tasks were intended and dropping them
loses coverage. For each task listed as missing a verifier:

1. Read its `instruction` in `{variant}-tasks.json` and study the app
   (`apps/{app-name}/server.py`, `js/`, seed data) to understand the relevant state.
2. Write the verifier at the exact path its `verify` field points to. The verifier
   must export `verify(server_url: str) -> tuple[bool, str]`, read `/api/state`, and
   check the task's success condition — it must never touch the UI. Follow the same
   structure as the existing verifier files in `{variant}-tasks/`.
3. Make sure the condition is actually achievable through the app's UI.

Only if a task genuinely cannot be verified (the app has no way to reach or observe
its end state) should you instead remove that task — and when you do, you MUST delete
BOTH its entry in `{variant}-tasks.json` AND any partial verifier file, so the two
stay in sync.

For any orphan verifier file with no json entry, either add the corresponding task to
`{variant}-tasks.json` (if it is a valid task) or delete the orphan file.

When done, run `apps/{app-name}/sanity_check_{variant}.py` (or `sanity_check.py`) and
make sure it passes. Do NOT edit unrelated app code.
