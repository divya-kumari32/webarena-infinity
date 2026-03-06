import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    reminders = state.get("invoiceReminders", [])
    overdue_reminders = [r for r in reminders if r["timing"] == "after"]

    if not overdue_reminders:
        return False, "No overdue (after-due-date) reminders found."

    for rem in overdue_reminders:
        if not rem.get("includeInvoicePdf"):
            return False, f"Overdue reminder (days={rem['days']}) does not include invoice PDF."

    return True, f"All {len(overdue_reminders)} overdue reminders include the invoice PDF."
