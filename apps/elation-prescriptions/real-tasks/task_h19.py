import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify interaction alerts set to major+moderate only AND allergy checking disabled."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    settings = state.get("settings", {})
    drug_decision_support = settings.get("drugDecisionSupport", {})

    errors = []

    # Check drugToDrugLevel is "major_moderate"
    drug_to_drug_level = drug_decision_support.get("drugToDrugLevel")
    if drug_to_drug_level == "all":
        errors.append(
            f"drugToDrugLevel is still 'all' (seed value). "
            f"Expected 'major_moderate'."
        )
    elif drug_to_drug_level != "major_moderate":
        # Accept common variations (case-insensitive)
        level_lower = (str(drug_to_drug_level) or "").lower().replace(" ", "_").replace("-", "_")
        if level_lower not in ["major_moderate", "major_and_moderate"]:
            errors.append(
                f"drugToDrugLevel is '{drug_to_drug_level}', expected 'major_moderate'."
            )

    # Check drugToAllergyEnabled is false
    drug_to_allergy_enabled = drug_decision_support.get("drugToAllergyEnabled")
    if drug_to_allergy_enabled is True:
        errors.append(
            f"drugToAllergyEnabled is still true (seed value). "
            f"Expected false."
        )
    elif drug_to_allergy_enabled is not False:
        errors.append(
            f"drugToAllergyEnabled is '{drug_to_allergy_enabled}', expected false."
        )

    if errors:
        return False, " | ".join(errors)

    return True, (
        f"Drug decision support settings updated successfully. "
        f"drugToDrugLevel='{drug_to_drug_level}', "
        f"drugToAllergyEnabled={drug_to_allergy_enabled}."
    )
