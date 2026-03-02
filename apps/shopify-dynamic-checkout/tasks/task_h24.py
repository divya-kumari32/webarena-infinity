import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])

    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found."

    vintage = next((t for t in themes if t.get("name") == "Vintage Revival"), None)
    if vintage is None:
        return False, "Theme 'Vintage Revival' not found."

    dawn_typo = dawn.get("settings", {}).get("typography", {})
    dawn_colors = dawn.get("settings", {}).get("colors", {})
    vintage_typo = vintage.get("settings", {}).get("typography", {})
    vintage_colors = vintage.get("settings", {}).get("colors", {})

    # Expected values from Vintage Revival seed data
    expected_heading = "Merriweather"
    expected_body = "Lora"
    expected_accent = "#8B4513"

    # Check heading font
    if dawn_typo.get("headingFont") != expected_heading:
        return False, (
            f"Expected Dawn headingFont to be '{expected_heading}' "
            f"(from Vintage Revival), but got '{dawn_typo.get('headingFont')}'."
        )

    # Check body font
    if dawn_typo.get("bodyFont") != expected_body:
        return False, (
            f"Expected Dawn bodyFont to be '{expected_body}' "
            f"(from Vintage Revival), but got '{dawn_typo.get('bodyFont')}'."
        )

    # Check accent color
    if dawn_colors.get("accentColor", "").upper() != expected_accent.upper():
        return False, (
            f"Expected Dawn accentColor to be '{expected_accent}' "
            f"(from Vintage Revival), but got '{dawn_colors.get('accentColor')}'."
        )

    return True, (
        f"Dawn typography updated with Vintage Revival fonts "
        f"(heading: {expected_heading}, body: {expected_body}) "
        f"and accent color set to {expected_accent}."
    )
