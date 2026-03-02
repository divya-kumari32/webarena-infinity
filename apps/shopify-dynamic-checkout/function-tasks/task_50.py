import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that all three fonts (heading, body, button) on Dawn are set to 'Montserrat'."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    dawn = next((t for t in themes if t["name"] == "Dawn"), None)
    if not dawn:
        return False, "Theme 'Dawn' not found."

    typography = dawn.get("settings", {}).get("typography", {})

    heading_font = typography.get("headingFont")
    if heading_font != "Montserrat":
        return False, f"Expected headingFont to be 'Montserrat', got '{heading_font}'."

    body_font = typography.get("bodyFont")
    if body_font != "Montserrat":
        return False, f"Expected bodyFont to be 'Montserrat', got '{body_font}'."

    button_font = typography.get("buttonFont")
    if button_font != "Montserrat":
        return False, f"Expected buttonFont to be 'Montserrat', got '{button_font}'."

    return True, "All three fonts (heading, body, button) on Dawn are set to 'Montserrat'."
