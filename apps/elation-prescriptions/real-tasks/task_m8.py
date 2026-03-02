import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Ciprofloxacin 500mg was discontinued from temporary meds."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    errors = []

    # Check that Ciprofloxacin 500mg is NOT in temporaryMeds
    temporary_meds = state.get("temporaryMeds", [])
    cipro_active = [
        m for m in temporary_meds
        if "ciprofloxacin" in m.get("medicationName", "").lower()
        and "500mg" in m.get("medicationName", "").lower()
    ]
    if cipro_active:
        errors.append(
            "Ciprofloxacin 500mg is still in temporaryMeds; expected it to be discontinued"
        )

    # Check that Ciprofloxacin 500mg IS in discontinuedMeds
    discontinued_meds = state.get("discontinuedMeds", [])
    cipro_disc = [
        m for m in discontinued_meds
        if "ciprofloxacin" in m.get("medicationName", "").lower()
        and "500mg" in m.get("medicationName", "").lower()
    ]
    if not cipro_disc:
        errors.append("Ciprofloxacin 500mg not found in discontinuedMeds")

    # Seed has 3 temp meds, should now have 2
    if len(temporary_meds) != 2:
        errors.append(
            f"Expected 2 temporaryMeds after discontinuation (seed had 3), found {len(temporary_meds)}"
        )

    if errors:
        return False, f"Ciprofloxacin discontinuation issues: {'; '.join(errors)}"

    return True, (
        "Ciprofloxacin 500mg successfully discontinued. "
        "Removed from temporaryMeds (now 2 remaining), added to discontinuedMeds."
    )
