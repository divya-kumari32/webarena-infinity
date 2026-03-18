import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Beta blocker updates: David's qty 90, Robert's dosage 25mg. Settings changes."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    errors = []

    # rx_016 David's Metoprolol -> quantity 90
    rx_016 = next((r for r in state["prescriptions"] if r["id"] == "rx_016"), None)
    if not rx_016:
        errors.append("Prescription rx_016 (Metoprolol, David) not found.")
    elif rx_016.get("quantity") != 90:
        errors.append(f"Expected rx_016 quantity 90, got {rx_016.get('quantity')}.")

    # rx_028 Robert's Carvedilol -> dosage 25mg
    rx_028 = next((r for r in state["prescriptions"] if r["id"] == "rx_028"), None)
    if not rx_028:
        errors.append("Prescription rx_028 (Carvedilol, Robert) not found.")
    elif rx_028.get("dosage") != "25mg":
        errors.append(f"Expected rx_028 dosage '25mg', got '{rx_028.get('dosage')}'.")

    settings = state.get("settings", {})
    if settings.get("defaultRefills") != 3:
        errors.append(f"Expected defaultRefills 3, got {settings.get('defaultRefills')}.")
    if settings.get("autoCheckInteractions") is not False:
        errors.append(f"Expected autoCheckInteractions False, got {settings.get('autoCheckInteractions')}.")

    if errors:
        return False, " ".join(errors)
    return True, "Beta blockers updated and settings changed correctly."
