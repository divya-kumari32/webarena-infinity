import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Medicare Part D patients: approve older's urgent refill, deny younger's Atorvastatin."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    errors = []

    # Older Medicare Part D patient = William (DOB 1944) -> approve rr_010 (urgent Furosemide)
    rr_010 = next((r for r in state["refillRequests"] if r["id"] == "rr_010"), None)
    if not rr_010:
        errors.append("Refill request rr_010 not found.")
    elif rr_010.get("status") != "approved":
        errors.append(f"Expected rr_010 (Furosemide, William) status 'approved', got '{rr_010.get('status')}'.")

    # Younger Medicare Part D patient = Margaret (DOB 1958) -> deny rr_001 (Atorvastatin)
    rr_001 = next((r for r in state["refillRequests"] if r["id"] == "rr_001"), None)
    if not rr_001:
        errors.append("Refill request rr_001 not found.")
    elif rr_001.get("status") != "denied":
        errors.append(f"Expected rr_001 (Atorvastatin, Margaret) status 'denied', got '{rr_001.get('status')}'.")

    if errors:
        return False, " ".join(errors)
    return True, "Older Medicare patient's urgent refill approved, younger's Atorvastatin denied."
