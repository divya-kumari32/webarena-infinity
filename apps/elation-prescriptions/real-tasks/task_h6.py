import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Doxycycline 100mg was prescribed as 14-day temporary to Walgreens."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    temporary_meds = state.get("temporaryMeds", [])
    errors = []

    # Find Doxycycline entry in temporaryMeds
    doxycycline_med = None
    for med in temporary_meds:
        med_name = med.get("medicationName", "")
        if "Doxycycline" in med_name and "100mg" in med_name:
            doxycycline_med = med
            break

    # Fallback: search by name only
    if doxycycline_med is None:
        for med in temporary_meds:
            if "Doxycycline" in med.get("medicationName", ""):
                doxycycline_med = med
                break

    if doxycycline_med is None:
        return False, "No medication containing 'Doxycycline' found in temporaryMeds"

    med_name = doxycycline_med.get("medicationName", "")

    # Check classification is temporary
    classification = doxycycline_med.get("classification", "")
    if classification != "temporary":
        errors.append(
            f"Doxycycline classification is '{classification}', expected 'temporary'"
        )

    # Check pharmacy contains Walgreens
    pharmacy_name = doxycycline_med.get("pharmacyName", "")
    if "Walgreens" not in pharmacy_name:
        errors.append(
            f"Doxycycline pharmacyName is '{pharmacy_name}', expected it to contain 'Walgreens'"
        )

    # Check daysSupply is 14
    days_supply = doxycycline_med.get("daysSupply")
    if days_supply != 14:
        errors.append(
            f"Doxycycline daysSupply is {days_supply}, expected 14"
        )

    # Check qty is 28 (100mg BID for 14 days = 28 tablets)
    qty = doxycycline_med.get("qty")
    if qty != 28:
        errors.append(
            f"Doxycycline qty is {qty}, expected 28"
        )

    # Check sig mentions twice daily or BID (case insensitive)
    sig = doxycycline_med.get("sig", "")
    sig_lower = sig.lower()
    if "twice daily" not in sig_lower and "bid" not in sig_lower and "twice a day" not in sig_lower and "2 times daily" not in sig_lower:
        errors.append(
            f"Doxycycline sig does not mention 'twice daily' or 'BID'. sig='{sig}'"
        )

    if errors:
        return False, "Failures: " + "; ".join(errors)

    return True, (
        f"Doxycycline 100mg prescribed as temporary successfully. "
        f"Medication: '{med_name}', pharmacy: '{pharmacy_name}', "
        f"daysSupply={days_supply}, qty={qty}, sig='{sig}'."
    )
