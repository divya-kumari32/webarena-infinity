import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Dawn's accentButtonBg is '#2563EB' and accentButtonText is '#FFFFFF'."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    dawn = next((t for t in themes if t["name"] == "Dawn"), None)
    if not dawn:
        return False, "Theme 'Dawn' not found."

    colors = dawn.get("settings", {}).get("colors", {})

    accent_bg = colors.get("accentButtonBg")
    if accent_bg != "#2563EB":
        return False, f"Expected accentButtonBg to be '#2563EB', got '{accent_bg}'."

    accent_text = colors.get("accentButtonText")
    if accent_text != "#FFFFFF":
        return False, f"Expected accentButtonText to be '#FFFFFF', got '{accent_text}'."

    return True, "Dawn's accentButtonBg is '#2563EB' and accentButtonText is '#FFFFFF'."
