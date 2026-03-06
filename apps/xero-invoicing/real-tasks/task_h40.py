import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    reminders = state.get("invoiceReminders", [])

    before_3 = next((r for r in reminders
                     if r["timing"] == "before" and r["days"] == 3), None)

    if not before_3:
        return False, "No 3-day before-due-date reminder found."

    if not before_3.get("enabled"):
        return False, "3-day before-due-date reminder is not enabled."

    return True, "3-day before-due-date invoice reminder added and enabled."
