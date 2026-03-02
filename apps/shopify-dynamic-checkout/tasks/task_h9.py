import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])

    # Find Dawn theme
    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found in state."

    dawn_settings = dawn.get("settings", {})
    dawn_colors = dawn_settings.get("colors", {})

    # Check button background is white
    accent_bg = dawn_colors.get("accentButtonBg", "")
    if accent_bg.upper() != "#FFFFFF":
        return False, (
            f"Expected Dawn accentButtonBg to be '#FFFFFF', but got '{accent_bg}'."
        )

    # Check button text is black
    accent_text = dawn_colors.get("accentButtonText", "")
    if accent_text.upper() != "#000000":
        return False, (
            f"Expected Dawn accentButtonText to be '#000000', but got '{accent_text}'."
        )

    # Check accent color matches Taste's accent color (#7C3AED)
    accent_color = dawn_colors.get("accentColor", "")
    if accent_color.upper() != "#7C3AED":
        return False, (
            f"Expected Dawn accentColor to be '#7C3AED' (Taste's accent color), "
            f"but got '{accent_color}'."
        )

    return True, (
        "Dawn button set to white bg (#FFFFFF) and black text (#000000), "
        "and accent color matches Taste (#7C3AED)."
    )
