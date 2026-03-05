import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Dawn's body font and button font are both changed to 'Roboto'."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    dawn = next((t for t in themes if t["name"] == "Dawn"), None)
    if not dawn:
        return False, "Theme 'Dawn' not found."

    typography = dawn.get("settings", {}).get("typography", {})

    actual_body = typography.get("bodyFont", "")
    if actual_body != "Roboto":
        return False, f"Expected bodyFont to be 'Roboto', got '{actual_body}'."

    actual_button = typography.get("buttonFont", "")
    if actual_button != "Roboto":
        return False, f"Expected buttonFont to be 'Roboto', got '{actual_button}'."

    return True, "Dawn's body font and button font are both 'Roboto'."
