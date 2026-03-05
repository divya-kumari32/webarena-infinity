import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that accelerated checkout is enabled on BOTH Craft templates (Default product and Product - Featured)."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    craft = next((t for t in themes if t["name"] == "Craft"), None)
    if not craft:
        return False, "Theme 'Craft' not found."

    templates = state.get("templates", [])

    default_product = next(
        (t for t in templates if t["name"] == "Default product" and t["themeId"] == craft["id"]),
        None,
    )
    if not default_product:
        return False, "Template 'Default product' for Craft theme not found."

    featured = next(
        (t for t in templates if t["name"] == "Product - Featured" and t["themeId"] == craft["id"]),
        None,
    )
    if not featured:
        return False, "Template 'Product - Featured' for Craft theme not found."

    if default_product.get("showAcceleratedCheckout") is not True:
        return False, f"Expected showAcceleratedCheckout to be true on 'Default product', got '{default_product.get('showAcceleratedCheckout')}'."

    if featured.get("showAcceleratedCheckout") is not True:
        return False, f"Expected showAcceleratedCheckout to be true on 'Product - Featured', got '{featured.get('showAcceleratedCheckout')}'."

    return True, "Accelerated checkout is enabled on both Craft templates (Default product and Product - Featured)."
