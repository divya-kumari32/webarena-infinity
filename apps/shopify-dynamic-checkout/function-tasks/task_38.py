import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Dawn's body font is 'Merriweather' and heading font is 'DM Serif Display'."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    dawn = next((t for t in themes if t["name"] == "Dawn"), None)
    if not dawn:
        return False, "Theme 'Dawn' not found."

    typography = dawn.get("settings", {}).get("typography", {})

    body_font = typography.get("bodyFont")
    if body_font != "Merriweather":
        return False, f"Expected Dawn body font to be 'Merriweather', got '{body_font}'."

    heading_font = typography.get("headingFont")
    if heading_font != "DM Serif Display":
        return False, f"Expected Dawn heading font to be 'DM Serif Display', got '{heading_font}'."

    return True, "Dawn's body font is 'Merriweather' and heading font is 'DM Serif Display'."
