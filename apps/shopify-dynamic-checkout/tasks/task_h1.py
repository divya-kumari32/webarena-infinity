import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    templates = state.get("templates", [])

    # Check Craft is published (role == 'main')
    craft = next((t for t in themes if t.get("name") == "Craft"), None)
    if craft is None:
        return False, "Theme 'Craft' not found in state."
    if craft.get("role") != "main":
        return False, f"Expected Craft theme role to be 'main', but got '{craft.get('role')}'."

    craft_id = craft.get("id")

    # Find Craft's Default product template and check showAcceleratedCheckout is True
    craft_default = next(
        (t for t in templates if t.get("themeId") == craft_id and t.get("isDefault") is True),
        None
    )
    if craft_default is None:
        return False, f"No default template found for Craft theme (themeId='{craft_id}')."
    if craft_default.get("showAcceleratedCheckout") is not True:
        return False, (
            f"Expected Craft default template '{craft_default.get('name')}' to have "
            f"showAcceleratedCheckout=True, but got '{craft_default.get('showAcceleratedCheckout')}'."
        )

    # Check Craft button background matches Dawn's original accent color (#4F46E5)
    craft_settings = craft.get("settings", {})
    craft_colors = craft_settings.get("colors", {})
    accent_bg = craft_colors.get("accentButtonBg", "")
    expected_color = "#4F46E5"
    if accent_bg.upper() != expected_color.upper():
        return False, (
            f"Expected Craft accentButtonBg to be '{expected_color}' (Dawn's accent color), "
            f"but got '{accent_bg}'."
        )

    return True, (
        "Craft is published, its default template has checkout enabled, "
        "and button background matches Dawn's accent color (#4F46E5)."
    )
