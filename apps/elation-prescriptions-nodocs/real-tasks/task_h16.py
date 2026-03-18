import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Check current patient is Aisha Rahman
    if state.get("currentPatientId") != "pat_003":
        return False, f"Expected currentPatientId 'pat_003' (Aisha Rahman), got '{state.get('currentPatientId')}'."

    prescriptions = state.get("prescriptions", [])
    seed_ids = {f"rx_{str(i).zfill(3)}" for i in range(1, 31)}
    errors = []

    # Find new Fluticasone prescription for pat_003
    flut_matches = [
        rx for rx in prescriptions
        if rx["id"] not in seed_ids
        and rx.get("patientId") == "pat_003"
        and "fluticasone" in rx.get("drugName", "").lower()
    ]

    if not flut_matches:
        errors.append("No new Fluticasone nasal spray prescription found for Aisha Rahman (pat_003).")
    else:
        flut = flut_matches[0]
        if flut.get("quantity") != 1:
            errors.append(f"Fluticasone: expected quantity 1, got {flut.get('quantity')}.")
        if flut.get("daysSupply") != 30:
            errors.append(f"Fluticasone: expected daysSupply 30, got {flut.get('daysSupply')}.")
        if flut.get("refillsTotal") != 2:
            errors.append(f"Fluticasone: expected refillsTotal 2, got {flut.get('refillsTotal')}.")
        if flut.get("pharmacyId") != "pharm_002":
            errors.append(f"Fluticasone: expected pharmacyId 'pharm_002' (Walgreens), got '{flut.get('pharmacyId')}'.")

    # Find new Montelukast prescription for pat_003
    mont_matches = [
        rx for rx in prescriptions
        if rx["id"] not in seed_ids
        and rx.get("patientId") == "pat_003"
        and "montelukast" in rx.get("drugName", "").lower()
    ]

    if not mont_matches:
        errors.append("No new Montelukast prescription found for Aisha Rahman (pat_003).")
    else:
        mont = mont_matches[0]
        if "10mg" not in mont.get("formStrength", "").lower().replace(" ", ""):
            errors.append(f"Montelukast: expected formStrength to contain '10mg', got '{mont.get('formStrength')}'.")
        if mont.get("quantity") != 30:
            errors.append(f"Montelukast: expected quantity 30, got {mont.get('quantity')}.")
        if mont.get("daysSupply") != 30:
            errors.append(f"Montelukast: expected daysSupply 30, got {mont.get('daysSupply')}.")
        if mont.get("refillsTotal") != 5:
            errors.append(f"Montelukast: expected refillsTotal 5, got {mont.get('refillsTotal')}.")
        if mont.get("pharmacyId") != "pharm_002":
            errors.append(f"Montelukast: expected pharmacyId 'pharm_002' (Walgreens), got '{mont.get('pharmacyId')}'.")

    if errors:
        return False, " ".join(errors)

    return True, "Fluticasone nasal spray and Montelukast 10mg prescribed correctly for Aisha Rahman, sent to Walgreens."
