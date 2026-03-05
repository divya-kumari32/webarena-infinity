import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Dawn's primaryBg is '#F0F0F0' and primaryText is '#333333'."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    dawn = next((t for t in themes if t["name"] == "Dawn"), None)
    if not dawn:
        return False, "Theme 'Dawn' not found."

    colors = dawn.get("settings", {}).get("colors", {})

    actual_bg = colors.get("primaryBg", "")
    if actual_bg.upper() != "#F0F0F0":
        return False, f"Expected primaryBg to be '#F0F0F0', got '{actual_bg}'."

    actual_text = colors.get("primaryText", "")
    if actual_text.upper() != "#333333":
        return False, f"Expected primaryText to be '#333333', got '{actual_text}'."

    return True, "Dawn's primaryBg is '#F0F0F0' and primaryText is '#333333'."
