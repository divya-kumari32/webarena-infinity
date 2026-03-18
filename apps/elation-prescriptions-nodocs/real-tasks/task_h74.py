import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Amlodipine 10mg, Atorvastatin qty 90, approve urgent refill, modify-approve Atorvastatin refill."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    errors = []

    # rx_002 Amlodipine dosage to 10mg
    rx_002 = next((r for r in state["prescriptions"] if r["id"] == "rx_002"), None)
    if not rx_002:
        errors.append("Prescription rx_002 (Amlodipine) not found.")
    elif rx_002.get("dosage") != "10mg":
        errors.append(f"Expected rx_002 dosage '10mg', got '{rx_002.get('dosage')}'.")

    # rx_001 Atorvastatin quantity to 90
    rx_001 = next((r for r in state["prescriptions"] if r["id"] == "rx_001"), None)
    if not rx_001:
        errors.append("Prescription rx_001 (Atorvastatin) not found.")
    elif rx_001.get("quantity") != 90:
        errors.append(f"Expected rx_001 quantity 90, got {rx_001.get('quantity')}.")

    # rr_003 urgent Pantoprazole -> approved
    rr_003 = next((r for r in state["refillRequests"] if r["id"] == "rr_003"), None)
    if not rr_003:
        errors.append("Refill request rr_003 not found.")
    elif rr_003.get("status") != "approved":
        errors.append(f"Expected rr_003 status 'approved', got '{rr_003.get('status')}'.")

    # rr_001 Atorvastatin -> modified
    rr_001 = next((r for r in state["refillRequests"] if r["id"] == "rr_001"), None)
    if not rr_001:
        errors.append("Refill request rr_001 not found.")
    else:
        if rr_001.get("status") != "modified":
            errors.append(f"Expected rr_001 status 'modified', got '{rr_001.get('status')}'.")
        if not rr_001.get("modifiedDetails"):
            errors.append("Expected rr_001 modifiedDetails to be set.")

    if errors:
        return False, " ".join(errors)
    return True, "Amlodipine and Atorvastatin updated, urgent refill approved, Atorvastatin refill modified."
