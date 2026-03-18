import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    errors = []

    # Check rr_003 (Pantoprazole refill) is modified with details containing "20mg"
    refill_requests = state.get("refillRequests", [])
    rr_003 = None
    for rr in refill_requests:
        if rr.get("id") == "rr_003":
            rr_003 = rr
            break

    if rr_003 is None:
        errors.append("Refill request rr_003 (Pantoprazole) not found.")
    else:
        if rr_003.get("status") != "modified":
            errors.append(f"Expected rr_003 status 'modified', got '{rr_003.get('status')}'.")
        modified_details = str(rr_003.get("modifiedDetails", ""))
        if "20mg" not in modified_details.lower():
            errors.append(f"Expected rr_003 modifiedDetails to contain '20mg', got '{modified_details}'.")

    # Check rx_005 (Pantoprazole 40mg) is discontinued
    prescriptions = state.get("prescriptions", [])
    rx_005 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_005":
            rx_005 = rx
            break

    if rx_005 is None:
        errors.append("Prescription rx_005 (Pantoprazole 40mg) not found.")
    elif rx_005.get("status") != "discontinued":
        errors.append(f"Expected rx_005 (Pantoprazole 40mg) status 'discontinued', got '{rx_005.get('status')}'.")

    if errors:
        return False, " ".join(errors)

    return True, "Pantoprazole refill modified-and-approved with step-down note, and current Pantoprazole 40mg discontinued."
