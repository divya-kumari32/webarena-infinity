import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Craft's Default product template has accelerated checkout enabled, Craft is published as main, and Dawn is no longer main."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])

    craft = next((t for t in themes if t["name"] == "Craft"), None)
    if not craft:
        return False, "Theme 'Craft' not found."

    dawn = next((t for t in themes if t["name"] == "Dawn"), None)
    if not dawn:
        return False, "Theme 'Dawn' not found."

    templates = state.get("templates", [])
    default_product = next(
        (t for t in templates if t["name"] == "Default product" and t["themeId"] == craft["id"]),
        None,
    )
    if not default_product:
        return False, "Template 'Default product' for Craft theme not found."

    if default_product.get("showAcceleratedCheckout") is not True:
        return False, f"Expected showAcceleratedCheckout to be true on Craft's 'Default product', got '{default_product.get('showAcceleratedCheckout')}'."

    if craft.get("role") != "main":
        return False, f"Expected Craft theme role to be 'main', got '{craft.get('role')}'."

    if dawn.get("role") == "main":
        return False, "Expected Dawn theme to no longer have role 'main', but it still does."

    return True, "Craft's Default product template has accelerated checkout enabled, Craft is published as main, and Dawn is no longer main."
