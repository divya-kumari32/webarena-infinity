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
    default_product = next(
        (t for t in templates if t.get("themeId") == craft_id and t.get("name") == "Default product"),
        None,
    )
    if default_product is None:
        return False, f"Template 'Default product' not found for Craft theme (id={craft_id})."

    if default_product.get("showAcceleratedCheckout") is not True:
        return (
            False,
            f"Expected showAcceleratedCheckout to be True on Craft's Default product template, "
            f"but got {default_product.get('showAcceleratedCheckout')}.",
        )

    return True, "Accelerated checkout is turned on for Craft theme's Default product template."
