import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found in state."

    settings = dawn.get("settings", {})
    typography = settings.get("typography", {})

    heading_font = typography.get("headingFont")
    if heading_font != "Inter":
        return (
            False,
            f"Expected Dawn headingFont to be 'Inter', but got '{heading_font}'.",
        )

    body_font = typography.get("bodyFont")
    if body_font != "Inter":
        return (
            False,
            f"Expected Dawn bodyFont to be 'Inter', but got '{body_font}'.",
        )

    button_font = typography.get("buttonFont")
    if button_font != "Inter":
        return (
            False,
            f"Expected Dawn buttonFont to be 'Inter', but got '{button_font}'.",
        )

    return True, "All three Dawn font settings (heading, body, button) are set to Inter."
