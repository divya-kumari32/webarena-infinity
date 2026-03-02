import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that accelerated checkout is enabled on Craft's Default product template."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    craft = next((t for t in themes if t["name"] == "Craft"), None)
    if not craft:
        return False, "Theme 'Craft' not found."

    templates = state.get("templates", [])
    template = next(
        (t for t in templates if t["name"] == "Default product" and t["themeId"] == craft["id"]),
        None,
    )
    if not template:
        return False, "Template 'Default product' for Craft theme not found."

    if template.get("showAcceleratedCheckout") is not True:
        return False, f"Expected showAcceleratedCheckout to be true, got '{template.get('showAcceleratedCheckout')}'."

    return True, "Accelerated checkout is enabled on Craft's Default product template."
