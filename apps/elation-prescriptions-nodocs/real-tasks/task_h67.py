import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Remove allergy-discontinued drug + other antibiotic from favorites."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    errors = []

    favs = state.get("settings", {}).get("favoritesDrugIds", [])

    # drug_025 Amoxicillin (discontinued due to allergic reaction) should be removed
    if "drug_025" in favs:
        errors.append("Amoxicillin (drug_025) is still in the favoritesDrugIds list.")

    # drug_028 Azithromycin (the other antibiotic in favorites) should be removed
    if "drug_028" in favs:
        errors.append("Azithromycin (drug_028) is still in the favoritesDrugIds list.")

    if errors:
        return False, " ".join(errors)
    return True, "Both antibiotics removed from favorites."
