import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Margaret's specialty pharmacy rx on hold + settings changes."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    errors = []

    # rx_030 Semaglutide (filled at BioPlus Specialty) -> on-hold
    rx_030 = next((r for r in state["prescriptions"] if r["id"] == "rx_030"), None)
    if not rx_030:
        errors.append("Prescription rx_030 (Semaglutide) not found.")
    elif rx_030.get("status") != "on-hold":
        errors.append(f"Expected rx_030 (Semaglutide) status 'on-hold', got '{rx_030.get('status')}'.")

    settings = state.get("settings", {})
    if settings.get("defaultPharmacy") != "pharm_009":
        errors.append(f"Expected defaultPharmacy 'pharm_009' (Capsule Pharmacy SF), got '{settings.get('defaultPharmacy')}'.")
    if settings.get("defaultRefills") != 5:
        errors.append(f"Expected defaultRefills 5, got {settings.get('defaultRefills')}.")

    if errors:
        return False, " ".join(errors)
    return True, "Specialty pharmacy rx on hold, settings updated correctly."
