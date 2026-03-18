import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Full settings overhaul + favorites reconfiguration."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    errors = []
    settings = state.get("settings", {})

    if settings.get("defaultPharmacy") != "pharm_015":
        errors.append(f"Expected defaultPharmacy 'pharm_015' (Optum Specialty), got '{settings.get('defaultPharmacy')}'.")
    if settings.get("defaultDaysSupply") != 90:
        errors.append(f"Expected defaultDaysSupply 90, got {settings.get('defaultDaysSupply')}.")
    if settings.get("defaultRefills") != 5:
        errors.append(f"Expected defaultRefills 5, got {settings.get('defaultRefills')}.")
    if settings.get("printFormat") != "detailed":
        errors.append(f"Expected printFormat 'detailed', got '{settings.get('printFormat')}'.")
    if settings.get("signatureRequired") is not False:
        errors.append(f"Expected signatureRequired False, got {settings.get('signatureRequired')}.")
    if settings.get("showGenericFirst") is not False:
        errors.append(f"Expected showGenericFirst False, got {settings.get('showGenericFirst')}.")

    favs = settings.get("favoritesDrugIds", [])
    if "drug_025" in favs:
        errors.append("Amoxicillin (drug_025) is still in favorites.")
    if "drug_028" in favs:
        errors.append("Azithromycin (drug_028) is still in favorites.")
    if "drug_035" not in favs:
        errors.append("Duloxetine (drug_035) not found in favorites.")
    if "drug_056" not in favs:
        errors.append("Fluoxetine (drug_056) not found in favorites.")

    if errors:
        return False, " ".join(errors)
    return True, "Settings overhauled and favorites reconfigured correctly."
