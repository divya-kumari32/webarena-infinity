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

    # Check headingFont matches Craft ('Playfair Display')
    heading_font = typography.get("headingFont", "")
    if heading_font != "Playfair Display":
        return False, (
            f"Expected Dawn headingFont to be 'Playfair Display' (matching Craft), "
            f"but got '{heading_font}'."
        )

    # Check bodyFont matches Craft ('Source Sans Pro')
    body_font = typography.get("bodyFont", "")
    if body_font != "Source Sans Pro":
        return False, (
            f"Expected Dawn bodyFont to be 'Source Sans Pro' (matching Craft), "
            f"but got '{body_font}'."
        )

    # Check headingScale is 110
    heading_scale = typography.get("headingScale")
    if heading_scale != 110:
        return False, (
            f"Expected Dawn headingScale to be 110, but got {heading_scale}."
        )

    return True, (
        "Dawn fonts updated to match Craft: headingFont='Playfair Display', "
        "bodyFont='Source Sans Pro', headingScale=110."
    )
