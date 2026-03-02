import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that drug-to-drug interaction alerts are set to show only major interactions."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    # Navigate to settings.drugDecisionSupport.drugToDrugLevel
    settings = state.get("settings", {})
    drug_decision_support = settings.get("drugDecisionSupport", {})

    if "drugToDrugLevel" not in drug_decision_support:
        return False, "settings.drugDecisionSupport.drugToDrugLevel field not found in state"

    drug_to_drug_level = drug_decision_support.get("drugToDrugLevel")

    if drug_to_drug_level != "major_only":
        return False, (
            f"settings.drugDecisionSupport.drugToDrugLevel is '{drug_to_drug_level}', "
            f"expected 'major_only'"
        )

    return True, "Drug-to-drug interaction alerts set to 'major_only' successfully."
