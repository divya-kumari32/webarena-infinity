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

    # Find new Advair Diskus prescription for pat_002
    # Advair contains Fluticasone/Salmeterol - check for any of these names
    seed_ids = {f"rx_{str(i).zfill(3)}" for i in range(1, 31)}
    matches = [
        rx for rx in prescriptions
        if rx["id"] not in seed_ids
        and rx.get("patientId") == "pat_002"
        and (
            "advair" in rx.get("drugName", "").lower()
            or "fluticasone" in rx.get("drugName", "").lower()
            or "salmeterol" in rx.get("drugName", "").lower()
        )
    ]

    if not matches:
        errors.append("No new Advair Diskus (Fluticasone/Salmeterol) prescription found for David Kowalski (pat_002).")
    else:
        new_rx = matches[0]
        form_strength = new_rx.get("formStrength", "").lower().replace(" ", "")
        if "250/50" not in form_strength and "250" not in form_strength:
            errors.append(f"Advair: expected formStrength to contain '250/50', got '{new_rx.get('formStrength')}'.")
        if new_rx.get("quantity") != 1:
            errors.append(f"Advair: expected quantity 1, got {new_rx.get('quantity')}.")
        if new_rx.get("daysSupply") != 30:
            errors.append(f"Advair: expected daysSupply 30, got {new_rx.get('daysSupply')}.")
        if new_rx.get("refillsTotal") != 2:
            errors.append(f"Advair: expected refillsTotal 2, got {new_rx.get('refillsTotal')}.")
        if new_rx.get("pharmacyId") != "pharm_003":
            errors.append(f"Advair: expected pharmacyId 'pharm_003' (Rite Aid), got '{new_rx.get('pharmacyId')}'.")

    # Check rr_005 (Metoprolol refill) is approved
    refill_requests = state.get("refillRequests", [])
    rr_005 = None
    for rr in refill_requests:
        if rr.get("id") == "rr_005":
            rr_005 = rr
            break

    if rr_005 is None:
        errors.append("Refill request rr_005 (Metoprolol) not found.")
    elif rr_005.get("status") != "approved":
        errors.append(f"Expected rr_005 (Metoprolol) status 'approved', got '{rr_005.get('status')}'.")

    if errors:
        return False, " ".join(errors)

    return True, "Advair Diskus 250/50 prescribed and Metoprolol refill approved for David Kowalski."
