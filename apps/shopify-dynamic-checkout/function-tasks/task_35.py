import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Dawn's secondaryBg is '#E5E7EB' and secondaryText is '#374151'."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    dawn = next((t for t in themes if t["name"] == "Dawn"), None)
    if not dawn:
        return False, "Theme 'Dawn' not found."

    colors = dawn.get("settings", {}).get("colors", {})

    secondary_bg = colors.get("secondaryBg")
    if secondary_bg != "#E5E7EB":
        return False, f"Expected Dawn secondaryBg to be '#E5E7EB', got '{secondary_bg}'."

    secondary_text = colors.get("secondaryText")
    if secondary_text != "#374151":
        return False, f"Expected Dawn secondaryText to be '#374151', got '{secondary_text}'."

    return True, "Dawn's secondaryBg is '#E5E7EB' and secondaryText is '#374151'."
