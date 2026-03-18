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

    # Find new Methylprednisolone prescription for pat_002
    seed_ids = {f"rx_{str(i).zfill(3)}" for i in range(1, 31)}
    matches = [
        rx for rx in prescriptions
        if rx["id"] not in seed_ids
        and rx.get("patientId") == "pat_002"
        and "methylprednisolone" in rx.get("drugName", "").lower()
    ]

    if not matches:
        errors.append("No new Methylprednisolone prescription found for David Kowalski (pat_002).")
    else:
        new_rx = matches[0]
        if new_rx.get("quantity") != 1:
            errors.append(f"Methylprednisolone: expected quantity 1, got {new_rx.get('quantity')}.")
        if new_rx.get("daysSupply") != 7:
            errors.append(f"Methylprednisolone: expected daysSupply 7, got {new_rx.get('daysSupply')}.")
        if new_rx.get("refillsTotal") != 0:
            errors.append(f"Methylprednisolone: expected refillsTotal 0, got {new_rx.get('refillsTotal')}.")
        if new_rx.get("pharmacyId") != "pharm_003":
            errors.append(f"Methylprednisolone: expected pharmacyId 'pharm_003' (Rite Aid), got '{new_rx.get('pharmacyId')}'.")

    # Check rx_018 (Escitalopram) is on-hold
    rx_018 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_018":
            rx_018 = rx
            break

    if rx_018 is None:
        errors.append("Prescription rx_018 (Escitalopram) not found.")
    elif rx_018.get("status") != "on-hold":
        errors.append(f"Expected rx_018 (Escitalopram) status 'on-hold', got '{rx_018.get('status')}'.")

    if errors:
        return False, " ".join(errors)

    return True, "Methylprednisolone dose pack prescribed and Escitalopram put on hold for David Kowalski."
