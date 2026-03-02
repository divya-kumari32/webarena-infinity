import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Dawn's accent button background color is changed to '#FF5733'."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    dawn = next((t for t in themes if t["name"] == "Dawn"), None)
    if not dawn:
        return False, "Theme 'Dawn' not found."

    colors = dawn.get("settings", {}).get("colors", {})
    actual = colors.get("accentButtonBg", "")

    if actual.upper() != "#FF5733":
        return False, f"Expected accentButtonBg to be '#FF5733', got '{actual}'."

    return True, "Dawn's accent button background color is '#FF5733'."
