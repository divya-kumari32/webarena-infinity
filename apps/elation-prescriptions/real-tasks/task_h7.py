import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Ondansetron 4mg was prescribed as temporary with correct details."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    temporary_meds = state.get("temporaryMeds", [])
    errors = []

    # Find Ondansetron entry in temporaryMeds
    ondansetron_med = None
    for med in temporary_meds:
        med_name = med.get("medicationName", "")
        if "Ondansetron" in med_name and "4mg" in med_name:
            ondansetron_med = med
            break

    # Fallback: search by name only
    if ondansetron_med is None:
        for med in temporary_meds:
            if "Ondansetron" in med.get("medicationName", ""):
                ondansetron_med = med
                break

    if ondansetron_med is None:
        return False, "No medication containing 'Ondansetron' found in temporaryMeds"

    med_name = ondansetron_med.get("medicationName", "")

    # Check classification is temporary
    classification = ondansetron_med.get("classification", "")
    if classification != "temporary":
        errors.append(
            f"Ondansetron classification is '{classification}', expected 'temporary'"
        )

    # Check qty is 12
    qty = ondansetron_med.get("qty")
    if qty != 12:
        errors.append(
            f"Ondansetron qty is {qty}, expected 12"
        )

    # Check daysSupply is 4
    days_supply = ondansetron_med.get("daysSupply")
    if days_supply != 4:
        errors.append(
            f"Ondansetron daysSupply is {days_supply}, expected 4"
        )

    # Check instructionsToPharmacy mentions "urgent" or "post-surgical" (case insensitive)
    instructions = ondansetron_med.get("instructionsToPharmacy", "")
    instructions_lower = instructions.lower()
    if "urgent" not in instructions_lower and "post-surgical" not in instructions_lower and "post surgical" not in instructions_lower and "postsurgical" not in instructions_lower:
        errors.append(
            f"Ondansetron instructionsToPharmacy does not mention 'urgent' or 'post-surgical'. "
            f"instructionsToPharmacy='{instructions}'"
        )

    if errors:
        return False, "Failures: " + "; ".join(errors)

    return True, (
        f"Ondansetron 4mg prescribed as temporary successfully. "
        f"Medication: '{med_name}', qty={qty}, daysSupply={days_supply}, "
        f"instructionsToPharmacy='{instructions}'."
    )
