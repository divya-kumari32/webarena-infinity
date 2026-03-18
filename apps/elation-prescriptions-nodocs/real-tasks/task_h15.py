import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Check current patient is William Thornton
    if state.get("currentPatientId") != "pat_004":
        return False, f"Expected currentPatientId 'pat_004' (William Thornton), got '{state.get('currentPatientId')}'."

    prescriptions = state.get("prescriptions", [])
    errors = []

    # Check rx_022 (Valsartan) renewed with 5 refills
    rx_022 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_022":
            rx_022 = rx
            break

    if rx_022 is None:
        errors.append("Prescription rx_022 (Valsartan) not found.")
    else:
        if rx_022.get("refillsRemaining") != 5:
            errors.append(f"Expected rx_022 (Valsartan) refillsRemaining 5, got {rx_022.get('refillsRemaining')}.")
        if rx_022.get("refillsTotal") != 5:
            errors.append(f"Expected rx_022 (Valsartan) refillsTotal 5, got {rx_022.get('refillsTotal')}.")
        if rx_022.get("status") != "active":
            errors.append(f"Expected rx_022 (Valsartan) status 'active', got '{rx_022.get('status')}'.")

    # Check rx_023 (Insulin Glargine) renewed with 3 refills
    rx_023 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_023":
            rx_023 = rx
            break

    if rx_023 is None:
        errors.append("Prescription rx_023 (Insulin Glargine) not found.")
    else:
        if rx_023.get("refillsRemaining") != 3:
            errors.append(f"Expected rx_023 (Insulin Glargine) refillsRemaining 3, got {rx_023.get('refillsRemaining')}.")
        if rx_023.get("refillsTotal") != 3:
            errors.append(f"Expected rx_023 (Insulin Glargine) refillsTotal 3, got {rx_023.get('refillsTotal')}.")
        if rx_023.get("status") != "active":
            errors.append(f"Expected rx_023 (Insulin Glargine) status 'active', got '{rx_023.get('status')}'.")

    if errors:
        return False, " ".join(errors)

    return True, "Valsartan renewed with 5 refills and Insulin Glargine renewed with 3 refills for William Thornton."
