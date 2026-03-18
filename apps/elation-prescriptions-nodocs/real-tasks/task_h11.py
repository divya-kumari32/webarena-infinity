import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Check current patient is Robert Fitzgerald
    if state.get("currentPatientId") != "pat_006":
        return False, f"Expected currentPatientId 'pat_006' (Robert Fitzgerald), got '{state.get('currentPatientId')}'."

    prescriptions = state.get("prescriptions", [])
    errors = []

    # Find new Dulaglutide prescription for pat_006
    seed_ids = {f"rx_{str(i).zfill(3)}" for i in range(1, 31)}
    matches = [
        rx for rx in prescriptions
        if rx["id"] not in seed_ids
        and rx.get("patientId") == "pat_006"
        and "dulaglutide" in rx.get("drugName", "").lower()
    ]

    if not matches:
        errors.append("No new Dulaglutide prescription found for Robert Fitzgerald (pat_006).")
    else:
        new_rx = matches[0]
        if new_rx.get("route") != "Subcutaneous":
            errors.append(f"Dulaglutide: expected route 'Subcutaneous', got '{new_rx.get('route')}'.")
        if new_rx.get("quantity") != 4:
            errors.append(f"Dulaglutide: expected quantity 4, got {new_rx.get('quantity')}.")
        if new_rx.get("daysSupply") != 28:
            errors.append(f"Dulaglutide: expected daysSupply 28, got {new_rx.get('daysSupply')}.")
        if new_rx.get("refillsTotal") != 2:
            errors.append(f"Dulaglutide: expected refillsTotal 2, got {new_rx.get('refillsTotal')}.")
        if new_rx.get("pharmacyId") != "pharm_004":
            errors.append(f"Dulaglutide: expected pharmacyId 'pharm_004' (UCSF Medical Center), got '{new_rx.get('pharmacyId')}'.")

    # Check rx_028 (Carvedilol) dosage contains "25"
    rx_028 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_028":
            rx_028 = rx
            break

    if rx_028 is None:
        errors.append("Prescription rx_028 (Carvedilol) not found.")
    elif "25" not in str(rx_028.get("dosage", "")):
        errors.append(f"Expected rx_028 (Carvedilol) dosage to contain '25', got '{rx_028.get('dosage')}'.")

    if errors:
        return False, " ".join(errors)

    return True, "Dulaglutide 0.75mg prescribed and Carvedilol increased to 25mg for Robert Fitzgerald."
