import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Rosuvastatin for David, Amlodipine for William."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    errors = []

    seed_ids = {f"rx_{str(i).zfill(3)}" for i in range(1, 31)}

    # New Rosuvastatin for David (pat_002)
    new_rosu = [
        rx for rx in state.get("prescriptions", [])
        if rx["id"] not in seed_ids
        and rx.get("patientId") == "pat_002"
        and "rosuvastatin" in rx.get("drugName", "").lower()
    ]
    if not new_rosu:
        errors.append("No new Rosuvastatin prescription found for David Kowalski (pat_002).")
    else:
        rx = new_rosu[0]
        if "10mg" not in rx.get("formStrength", "").lower().replace(" ", ""):
            errors.append(f"Expected Rosuvastatin formStrength containing '10mg', got '{rx.get('formStrength')}'.")
        if rx.get("quantity") != 90:
            errors.append(f"Expected Rosuvastatin quantity 90, got {rx.get('quantity')}.")
        if rx.get("daysSupply") != 90:
            errors.append(f"Expected Rosuvastatin daysSupply 90, got {rx.get('daysSupply')}.")
        if rx.get("refillsTotal") != 3:
            errors.append(f"Expected Rosuvastatin refillsTotal 3, got {rx.get('refillsTotal')}.")
        if rx.get("pharmacyId") != "pharm_003":
            errors.append(f"Expected Rosuvastatin pharmacyId 'pharm_003' (Rite Aid), got '{rx.get('pharmacyId')}'.")

    # New Amlodipine for William (pat_004)
    new_amlo = [
        rx for rx in state.get("prescriptions", [])
        if rx["id"] not in seed_ids
        and rx.get("patientId") == "pat_004"
        and "amlodipine" in rx.get("drugName", "").lower()
    ]
    if not new_amlo:
        errors.append("No new Amlodipine prescription found for William Thornton (pat_004).")
    else:
        rx = new_amlo[0]
        if "5mg" not in rx.get("formStrength", "").lower().replace(" ", ""):
            errors.append(f"Expected Amlodipine formStrength containing '5mg', got '{rx.get('formStrength')}'.")
        if rx.get("quantity") != 30:
            errors.append(f"Expected Amlodipine quantity 30, got {rx.get('quantity')}.")
        if rx.get("refillsTotal") != 5:
            errors.append(f"Expected Amlodipine refillsTotal 5, got {rx.get('refillsTotal')}.")
        if rx.get("pharmacyId") != "pharm_005":
            errors.append(f"Expected Amlodipine pharmacyId 'pharm_005' (Kaiser), got '{rx.get('pharmacyId')}'.")

    # Current patient should be William (last switch)
    if state.get("currentPatientId") != "pat_004":
        errors.append(f"Expected currentPatientId 'pat_004' (William Thornton), got '{state.get('currentPatientId')}'.")

    if errors:
        return False, " ".join(errors)
    return True, "Rosuvastatin prescribed for David and Amlodipine prescribed for William."
