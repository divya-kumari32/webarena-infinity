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
    if heading_font != "Playfair Display":
        return (
            False,
            f"Expected Dawn headingFont to be 'Playfair Display', but got '{heading_font}'.",
        )

    body_font = typography.get("bodyFont")
    if body_font != "Source Sans Pro":
        return (
            False,
            f"Expected Dawn bodyFont to be 'Source Sans Pro', but got '{body_font}'.",
        )

    return True, "Dawn heading font is Playfair Display and body font is Source Sans Pro."
