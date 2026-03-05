import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Dawn's heading font is changed to 'Playfair Display'."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    dawn = next((t for t in themes if t["name"] == "Dawn"), None)
    if not dawn:
        return False, "Theme 'Dawn' not found."

    typography = dawn.get("settings", {}).get("typography", {})
    actual = typography.get("headingFont", "")

    if actual != "Playfair Display":
        return False, f"Expected headingFont to be 'Playfair Display', got '{actual}'."

    return True, "Dawn's heading font is 'Playfair Display'."
