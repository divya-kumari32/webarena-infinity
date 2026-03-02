import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    templates = state.get("templates", [])

    # Check Taste is published (role == 'main')
    taste = next((t for t in themes if t.get("name") == "Taste"), None)
    if taste is None:
        return False, "Theme 'Taste' not found in state."
    if taste.get("role") != "main":
        return False, (
            f"Expected Taste theme role to be 'main', but got '{taste.get('role')}'."
        )
    taste_id = taste.get("id")

    # Check Taste default template has checkout enabled
    taste_default = next(
        (t for t in templates if t.get("themeId") == taste_id and t.get("isDefault") is True),
        None
    )
    if taste_default is None:
        return False, f"No default template found for Taste theme (themeId='{taste_id}')."
    if taste_default.get("showAcceleratedCheckout") is not True:
        return False, (
            f"Expected Taste default template to have showAcceleratedCheckout=True, "
            f"but got '{taste_default.get('showAcceleratedCheckout')}'."
        )

    # Check Taste button font is 'Oswald'
    taste_settings = taste.get("settings", {})
    typography = taste_settings.get("typography", {})
    button_font = typography.get("buttonFont", "")
    if button_font != "Oswald":
        return False, (
            f"Expected Taste buttonFont to be 'Oswald', but got '{button_font}'."
        )

    return True, (
        "Taste is published, its default template has checkout enabled, "
        "and button font changed to Oswald."
    )
