import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Aspirin-allergy patient statin to 80mg, NKDA patient gets Amlodipine."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    errors = []

    # David Kowalski (Aspirin allergy) — rx_017 Atorvastatin dosage to 80mg
    rx_017 = next((r for r in state["prescriptions"] if r["id"] == "rx_017"), None)
    if not rx_017:
        errors.append("Prescription rx_017 (Atorvastatin, David) not found.")
    elif rx_017.get("dosage") != "80mg":
        errors.append(f"Expected rx_017 dosage '80mg', got '{rx_017.get('dosage')}'.")

    # Aisha Rahman (NKDA) — new Amlodipine prescription
    if state.get("currentPatientId") != "pat_003":
        errors.append(f"Expected currentPatientId 'pat_003' (Aisha Rahman), got '{state.get('currentPatientId')}'.")

    seed_ids = {f"rx_{str(i).zfill(3)}" for i in range(1, 31)}
    new_amlodipine = [
        rx for rx in state.get("prescriptions", [])
        if rx["id"] not in seed_ids
        and rx.get("patientId") == "pat_003"
        and "amlodipine" in rx.get("drugName", "").lower()
    ]
    if not new_amlodipine:
        errors.append("No new Amlodipine prescription found for Aisha Rahman (pat_003).")
    else:
        rx = new_amlodipine[0]
        if rx.get("quantity") != 30:
            errors.append(f"Expected Amlodipine quantity 30, got {rx.get('quantity')}.")
        if rx.get("refillsTotal") != 5:
            errors.append(f"Expected Amlodipine refillsTotal 5, got {rx.get('refillsTotal')}.")
        if rx.get("pharmacyId") != "pharm_002":
            errors.append(f"Expected Amlodipine pharmacyId 'pharm_002' (Walgreens), got '{rx.get('pharmacyId')}'.")

    if errors:
        return False, " ".join(errors)
    return True, "David's statin increased to 80mg and Amlodipine prescribed for Aisha."
