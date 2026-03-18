import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Discontinue Pantoprazole, prescribe Esomeprazole, compact print format."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    errors = []

    # rx_005 Pantoprazole -> discontinued
    rx_005 = next((r for r in state["prescriptions"] if r["id"] == "rx_005"), None)
    if not rx_005:
        errors.append("Prescription rx_005 (Pantoprazole) not found.")
    elif rx_005.get("status") != "discontinued":
        errors.append(f"Expected rx_005 (Pantoprazole) status 'discontinued', got '{rx_005.get('status')}'.")

    # New Esomeprazole prescription for Margaret
    seed_ids = {f"rx_{str(i).zfill(3)}" for i in range(1, 31)}
    new_esomeprazole = [
        rx for rx in state.get("prescriptions", [])
        if rx["id"] not in seed_ids
        and rx.get("patientId") == "pat_001"
        and "esomeprazole" in rx.get("drugName", "").lower()
    ]
    if not new_esomeprazole:
        errors.append("No new Esomeprazole prescription found for Margaret Chen.")
    else:
        rx = new_esomeprazole[0]
        if "20mg" not in rx.get("formStrength", "").lower().replace(" ", ""):
            errors.append(f"Expected Esomeprazole formStrength containing '20mg', got '{rx.get('formStrength')}'.")
        if rx.get("frequency") != "Once daily":
            errors.append(f"Expected Esomeprazole frequency 'Once daily', got '{rx.get('frequency')}'.")
        if rx.get("quantity") != 30:
            errors.append(f"Expected Esomeprazole quantity 30, got {rx.get('quantity')}.")
        if rx.get("refillsTotal") != 2:
            errors.append(f"Expected Esomeprazole refillsTotal 2, got {rx.get('refillsTotal')}.")
        if rx.get("pharmacyId") != "pharm_001":
            errors.append(f"Expected Esomeprazole pharmacyId 'pharm_001' (CVS), got '{rx.get('pharmacyId')}'.")

    # Print format compact
    if state.get("settings", {}).get("printFormat") != "compact":
        errors.append(f"Expected printFormat 'compact', got '{state.get('settings', {}).get('printFormat')}'.")

    if errors:
        return False, " ".join(errors)
    return True, "Pantoprazole discontinued, Esomeprazole prescribed, print format compact."
