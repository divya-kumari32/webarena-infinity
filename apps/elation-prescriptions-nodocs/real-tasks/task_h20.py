import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    prescriptions = state.get("prescriptions", [])
    errors = []

    # Check rx_006 (Albuterol) status is "cancelled"
    rx_006 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_006":
            rx_006 = rx
            break

    if rx_006 is None:
        errors.append("Prescription rx_006 (Albuterol) not found.")
    elif rx_006.get("status") != "cancelled":
        errors.append(f"Expected rx_006 (Albuterol) status 'cancelled', got '{rx_006.get('status')}'.")

    # Check rx_008 (Flonase) status is "on-hold"
    rx_008 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_008":
            rx_008 = rx
            break

    if rx_008 is None:
        errors.append("Prescription rx_008 (Flonase) not found.")
    elif rx_008.get("status") != "on-hold":
        errors.append(f"Expected rx_008 (Flonase) status 'on-hold', got '{rx_008.get('status')}'.")

    # Check rx_001 (Atorvastatin) renewed with 3 refills
    rx_001 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_001":
            rx_001 = rx
            break

    if rx_001 is None:
        errors.append("Prescription rx_001 (Atorvastatin) not found.")
    else:
        if rx_001.get("refillsRemaining") != 3:
            errors.append(f"Expected rx_001 (Atorvastatin) refillsRemaining 3, got {rx_001.get('refillsRemaining')}.")
        if rx_001.get("refillsTotal") != 3:
            errors.append(f"Expected rx_001 (Atorvastatin) refillsTotal 3, got {rx_001.get('refillsTotal')}.")
        if rx_001.get("status") != "active":
            errors.append(f"Expected rx_001 (Atorvastatin) status 'active', got '{rx_001.get('status')}'.")

    if errors:
        return False, " ".join(errors)

    return True, "Albuterol cancelled, Flonase put on hold, and Atorvastatin renewed with 3 refills for Margaret."
