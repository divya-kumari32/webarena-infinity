import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Check current patient is David Kowalski
    if state.get("currentPatientId") != "pat_002":
        return False, f"Expected currentPatientId 'pat_002' (David Kowalski), got '{state.get('currentPatientId')}'."

    prescriptions = state.get("prescriptions", [])
    errors = []

    # Check rx_018 (Escitalopram) dosage contains "5"
    rx_018 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_018":
            rx_018 = rx
            break

    if rx_018 is None:
        errors.append("Prescription rx_018 (Escitalopram) not found.")
    elif "5" not in str(rx_018.get("dosage", "")):
        errors.append(f"Expected rx_018 (Escitalopram) dosage to contain '5', got '{rx_018.get('dosage')}'.")

    # Check rx_019 (Metformin ER) frequency is "Twice daily"
    rx_019 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_019":
            rx_019 = rx
            break

    if rx_019 is None:
        errors.append("Prescription rx_019 (Metformin ER) not found.")
    elif rx_019.get("frequency") != "Twice daily":
        errors.append(f"Expected rx_019 (Metformin ER) frequency 'Twice daily', got '{rx_019.get('frequency')}'.")

    if errors:
        return False, " ".join(errors)

    return True, "Escitalopram reduced to 5mg and Metformin ER changed to twice daily for David Kowalski."
