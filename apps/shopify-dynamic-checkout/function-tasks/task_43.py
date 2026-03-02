import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that a 'Product - Limited Edition' template was created on Dawn with accelerated checkout enabled."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    dawn = next((t for t in themes if t["name"] == "Dawn"), None)
    if not dawn:
        return False, "Theme 'Dawn' not found."

    templates = state.get("templates", [])
    limited_edition = next(
        (t for t in templates if t["name"] == "Product - Limited Edition" and t["themeId"] == dawn["id"]),
        None,
    )
    if not limited_edition:
        return False, "Template 'Product - Limited Edition' not found on Dawn theme."

    if limited_edition.get("isAlternate") is not True:
        return False, f"Expected isAlternate to be true on 'Product - Limited Edition', got '{limited_edition.get('isAlternate')}'."

    if limited_edition.get("showAcceleratedCheckout") is not True:
        return False, f"Expected showAcceleratedCheckout to be true on 'Product - Limited Edition', got '{limited_edition.get('showAcceleratedCheckout')}'."

    return True, "Template 'Product - Limited Edition' created on Dawn with isAlternate=true and showAcceleratedCheckout=true."
