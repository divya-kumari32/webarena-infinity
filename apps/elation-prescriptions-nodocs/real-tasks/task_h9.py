import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    prescriptions = state.get("prescriptions", [])
    errors = []

    # Find new Cyclobenzaprine prescription for pat_001
    seed_ids = {f"rx_{str(i).zfill(3)}" for i in range(1, 31)}
    matches = [
        rx for rx in prescriptions
        if rx["id"] not in seed_ids
        and rx.get("patientId") == "pat_001"
        and "cyclobenzaprine" in rx.get("drugName", "").lower()
    ]

    if not matches:
        errors.append("No new Cyclobenzaprine prescription found for Margaret (pat_001).")
    else:
        new_rx = matches[0]
        if "10mg" not in new_rx.get("formStrength", "").lower().replace(" ", ""):
            errors.append(f"Cyclobenzaprine: expected formStrength to contain '10mg', got '{new_rx.get('formStrength')}'.")
        if new_rx.get("frequency") != "Three times daily":
            errors.append(f"Cyclobenzaprine: expected frequency 'Three times daily', got '{new_rx.get('frequency')}'.")
        if new_rx.get("quantity") != 30:
            errors.append(f"Cyclobenzaprine: expected quantity 30, got {new_rx.get('quantity')}.")
        if new_rx.get("daysSupply") != 10:
            errors.append(f"Cyclobenzaprine: expected daysSupply 10, got {new_rx.get('daysSupply')}.")
        if new_rx.get("refillsTotal") != 0:
            errors.append(f"Cyclobenzaprine: expected refillsTotal 0, got {new_rx.get('refillsTotal')}.")
        if new_rx.get("pharmacyId") != "pharm_001":
            errors.append(f"Cyclobenzaprine: expected pharmacyId 'pharm_001' (CVS), got '{new_rx.get('pharmacyId')}'.")

    # Check rx_007 (Gabapentin) dosage contains "400"
    rx_007 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_007":
            rx_007 = rx
            break

    if rx_007 is None:
        errors.append("Prescription rx_007 (Gabapentin) not found.")
    elif "400" not in str(rx_007.get("dosage", "")):
        errors.append(f"Expected rx_007 (Gabapentin) dosage to contain '400', got '{rx_007.get('dosage')}'.")

    if errors:
        return False, " ".join(errors)

    return True, "Cyclobenzaprine 10mg prescribed and Gabapentin increased to 400mg for Margaret."
