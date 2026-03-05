import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    craft = next((t for t in themes if t.get("name") == "Craft"), None)
    if craft is None:
        return False, "Theme 'Craft' not found in state."
    craft_id = craft.get("id")

    templates = state.get("templates", [])

    default_tmpl = next(
        (t for t in templates if t.get("themeId") == craft_id and t.get("name") == "Default product"),
        None,
    )
    if default_tmpl is None:
        return False, f"Template 'Default product' not found for Craft theme (id={craft_id})."

    if default_tmpl.get("showAcceleratedCheckout") is not False:
        return (
            False,
            f"Expected Craft 'Default product' showAcceleratedCheckout to be False, "
            f"but got {default_tmpl.get('showAcceleratedCheckout')}.",
        )

    featured_tmpl = next(
        (t for t in templates if t.get("themeId") == craft_id and t.get("name") == "Product - Featured"),
        None,
    )
    if featured_tmpl is None:
        return False, f"Template 'Product - Featured' not found for Craft theme (id={craft_id})."

    if featured_tmpl.get("showAcceleratedCheckout") is not False:
        return (
            False,
            f"Expected Craft 'Product - Featured' showAcceleratedCheckout to be False, "
            f"but got {featured_tmpl.get('showAcceleratedCheckout')}.",
        )

    return True, "Checkout is turned off on both Craft templates (Default product and Product - Featured)."
