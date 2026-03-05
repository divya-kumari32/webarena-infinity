import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Dark theme: Dawn primary/secondary colors + heading/body fonts."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found."

    colors = dawn.get("settings", {}).get("colors", {})
    typo = dawn.get("settings", {}).get("typography", {})

    checks = [
        ("primaryBg", "#0F172A"),
        ("primaryText", "#F8FAFC"),
        ("secondaryBg", "#1E293B"),
        ("secondaryText", "#94A3B8"),
    ]
    for key, expected in checks:
        actual = colors.get(key, "")
        if actual.upper() != expected.upper():
            return False, f"Expected Dawn {key}='{expected}', got '{actual}'."

    if typo.get("headingFont") != "DM Serif Display":
        return False, f"Expected heading font 'DM Serif Display', got '{typo.get('headingFont')}'."
    if typo.get("bodyFont") != "DM Sans":
        return False, f"Expected body font 'DM Sans', got '{typo.get('bodyFont')}'."

    return True, ("Dawn dark theme applied: #0F172A/#F8FAFC primary, "
                  "#1E293B/#94A3B8 secondary. Fonts: DM Serif Display/DM Sans.")
