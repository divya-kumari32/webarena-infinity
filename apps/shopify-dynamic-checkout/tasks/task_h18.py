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
    typography = dawn_settings.get("typography", {})

    # Check headingFont matches Sense ('DM Serif Display')
    heading_font = typography.get("headingFont", "")
    if heading_font != "DM Serif Display":
        return False, (
            f"Expected Dawn headingFont to be 'DM Serif Display' (matching Sense), "
            f"but got '{heading_font}'."
        )

    # Check bodyFont matches Sense ('DM Sans')
    body_font = typography.get("bodyFont", "")
    if body_font != "DM Sans":
        return False, (
            f"Expected Dawn bodyFont to be 'DM Sans' (matching Sense), "
            f"but got '{body_font}'."
        )

    # Check bodyScale is 95
    body_scale = typography.get("bodyScale")
    if body_scale != 95:
        return False, (
            f"Expected Dawn bodyScale to be 95, but got {body_scale}."
        )

    return True, (
        "Dawn fonts updated to match Sense: headingFont='DM Serif Display', "
        "bodyFont='DM Sans', bodyScale=95."
    )
