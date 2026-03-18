import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Urgent refill modified-approved, all other pending refills denied."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    errors = []

    # rr_003 (urgent, patient ran out) -> modified
    rr_003 = next((r for r in state["refillRequests"] if r["id"] == "rr_003"), None)
    if not rr_003:
        errors.append("Refill request rr_003 not found.")
    else:
        if rr_003.get("status") != "modified":
            errors.append(f"Expected rr_003 status 'modified', got '{rr_003.get('status')}'.")
        if not rr_003.get("modifiedDetails"):
            errors.append("Expected rr_003 modifiedDetails to be set.")

    # All other Margaret pending refills -> denied
    for rr_id in ["rr_001", "rr_002", "rr_011"]:
        rr = next((r for r in state["refillRequests"] if r["id"] == rr_id), None)
        if not rr:
            errors.append(f"Refill request {rr_id} not found.")
        elif rr.get("status") != "denied":
            errors.append(f"Expected {rr_id} status 'denied', got '{rr.get('status')}'.")

    if errors:
        return False, " ".join(errors)
    return True, "Urgent refill modified-approved, all routine refills denied."
