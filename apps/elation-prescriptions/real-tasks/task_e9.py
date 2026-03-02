import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that drug-to-allergy alerts have been turned off in settings."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    # Navigate to settings.drugDecisionSupport.drugToAllergyEnabled
    settings = state.get("settings", {})
    drug_decision_support = settings.get("drugDecisionSupport", {})

    if "drugToAllergyEnabled" not in drug_decision_support:
        return False, "settings.drugDecisionSupport.drugToAllergyEnabled field not found in state"

    drug_to_allergy_enabled = drug_decision_support.get("drugToAllergyEnabled")

    if drug_to_allergy_enabled is not False:
        return False, (
            f"settings.drugDecisionSupport.drugToAllergyEnabled is "
            f"'{drug_to_allergy_enabled}' (type: {type(drug_to_allergy_enabled).__name__}), "
            f"expected false"
        )

    return True, "Drug-to-allergy alerts successfully turned off (drugToAllergyEnabled=false)."
