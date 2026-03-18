import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Discontinue Robert's diabetes med, hold William's insulin, approve Margaret's urgent refill."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    errors = []

    # rx_027 Empagliflozin (Robert's diabetes med) -> discontinued
    rx_027 = next((r for r in state["prescriptions"] if r["id"] == "rx_027"), None)
    if not rx_027:
        errors.append("Prescription rx_027 (Empagliflozin) not found.")
    elif rx_027.get("status") != "discontinued":
        errors.append(f"Expected rx_027 (Empagliflozin) status 'discontinued', got '{rx_027.get('status')}'.")

    # rx_023 Insulin Glargine (William) -> on-hold
    rx_023 = next((r for r in state["prescriptions"] if r["id"] == "rx_023"), None)
    if not rx_023:
        errors.append("Prescription rx_023 (Insulin Glargine) not found.")
    elif rx_023.get("status") != "on-hold":
        errors.append(f"Expected rx_023 (Insulin Glargine) status 'on-hold', got '{rx_023.get('status')}'.")

    # rr_003 Margaret's urgent Pantoprazole -> approved
    rr_003 = next((r for r in state["refillRequests"] if r["id"] == "rr_003"), None)
    if not rr_003:
        errors.append("Refill request rr_003 not found.")
    elif rr_003.get("status") != "approved":
        errors.append(f"Expected rr_003 (Pantoprazole urgent) status 'approved', got '{rr_003.get('status')}'.")

    if errors:
        return False, " ".join(errors)
    return True, "Robert's Empagliflozin discontinued, William's insulin on hold, Margaret's urgent refill approved."
