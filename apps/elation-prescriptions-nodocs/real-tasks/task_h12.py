import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    settings = state.get("settings", {})
    errors = []

    # Check showGenericFirst is False (brand names shown first)
    if settings.get("showGenericFirst") is not False:
        errors.append(f"Expected showGenericFirst False, got {settings.get('showGenericFirst')}.")

    # Check default pharmacy is Alto Pharmacy (pharm_007)
    if settings.get("defaultPharmacy") != "pharm_007":
        errors.append(f"Expected defaultPharmacy 'pharm_007' (Alto Pharmacy), got '{settings.get('defaultPharmacy')}'.")

    # Check Pantoprazole (drug_019) NOT in favorites
    favorites = settings.get("favoritesDrugIds", [])
    if "drug_019" in favorites:
        errors.append("Expected 'drug_019' (Pantoprazole) to be removed from favoritesDrugIds, but it is still present.")

    # Check Atorvastatin (drug_001) NOT in favorites
    if "drug_001" in favorites:
        errors.append("Expected 'drug_001' (Atorvastatin) to be removed from favoritesDrugIds, but it is still present.")

    if errors:
        return False, " ".join(errors)

    return True, "Settings updated: brand names first, Alto Pharmacy default, Pantoprazole and Atorvastatin removed from favorites."
