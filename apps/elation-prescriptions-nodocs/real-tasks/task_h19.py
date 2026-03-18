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

    # Check rx_029 (Spironolactone) dosage contains "50"
    rx_029 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_029":
            rx_029 = rx
            break

    if rx_029 is None:
        errors.append("Prescription rx_029 (Spironolactone) not found.")
    elif "50" not in str(rx_029.get("dosage", "")):
        errors.append(f"Expected rx_029 (Spironolactone) dosage to contain '50', got '{rx_029.get('dosage')}'.")

    # Check rx_028 (Carvedilol) quantity == 90
    rx_028 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_028":
            rx_028 = rx
            break

    if rx_028 is None:
        errors.append("Prescription rx_028 (Carvedilol) not found.")
    elif rx_028.get("quantity") != 90:
        errors.append(f"Expected rx_028 (Carvedilol) quantity 90, got {rx_028.get('quantity')}.")

    # Find new Furosemide prescription for pat_006
    seed_ids = {f"rx_{str(i).zfill(3)}" for i in range(1, 31)}
    matches = [
        rx for rx in prescriptions
        if rx["id"] not in seed_ids
        and rx.get("patientId") == "pat_006"
        and "furosemide" in rx.get("drugName", "").lower()
    ]

    if not matches:
        errors.append("No new Furosemide prescription found for Robert Fitzgerald (pat_006).")
    else:
        new_rx = matches[0]
        if "20mg" not in new_rx.get("formStrength", "").lower().replace(" ", ""):
            errors.append(f"Furosemide: expected formStrength to contain '20mg', got '{new_rx.get('formStrength')}'.")
        if new_rx.get("quantity") != 30:
            errors.append(f"Furosemide: expected quantity 30, got {new_rx.get('quantity')}.")
        if new_rx.get("daysSupply") != 30:
            errors.append(f"Furosemide: expected daysSupply 30, got {new_rx.get('daysSupply')}.")
        if new_rx.get("refillsTotal") != 5:
            errors.append(f"Furosemide: expected refillsTotal 5, got {new_rx.get('refillsTotal')}.")
        if new_rx.get("pharmacyId") != "pharm_004":
            errors.append(f"Furosemide: expected pharmacyId 'pharm_004' (UCSF Medical Center), got '{new_rx.get('pharmacyId')}'.")

    if errors:
        return False, " ".join(errors)

    return True, "Spironolactone increased to 50mg, Carvedilol quantity set to 90, and Furosemide 20mg prescribed for Robert Fitzgerald."
