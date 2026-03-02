import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Escitalopram 10mg was prescribed via Alto Pharmacy with 5 refills and 30-day supply."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    permanent_rx_meds = state.get("permanentRxMeds", [])
    errors = []

    # Find Escitalopram 10mg entry in permanentRxMeds
    escitalopram_med = None
    for med in permanent_rx_meds:
        med_name = med.get("medicationName", "")
        if "Escitalopram" in med_name and "10mg" in med_name:
            escitalopram_med = med
            break

    # Fallback: search by name only
    if escitalopram_med is None:
        for med in permanent_rx_meds:
            if "Escitalopram" in med.get("medicationName", ""):
                escitalopram_med = med
                break

    if escitalopram_med is None:
        return False, "No medication containing 'Escitalopram' found in permanentRxMeds"

    med_name = escitalopram_med.get("medicationName", "")

    # Check pharmacyName contains Alto
    pharmacy_name = escitalopram_med.get("pharmacyName", "")
    if "Alto" not in pharmacy_name:
        errors.append(
            f"Escitalopram pharmacyName is '{pharmacy_name}', expected it to contain 'Alto'"
        )

    # Check refills is 5
    refills = escitalopram_med.get("refills")
    if refills != 5:
        errors.append(
            f"Escitalopram refills is {refills}, expected 5"
        )

    # Check daysSupply is 30
    days_supply = escitalopram_med.get("daysSupply")
    if days_supply != 30:
        errors.append(
            f"Escitalopram daysSupply is {days_supply}, expected 30"
        )

    if errors:
        return False, "Failures: " + "; ".join(errors)

    return True, (
        f"Escitalopram 10mg prescribed successfully via Alto Pharmacy. "
        f"Medication: '{med_name}', pharmacy: '{pharmacy_name}', "
        f"refills={refills}, daysSupply={days_supply}."
    )
