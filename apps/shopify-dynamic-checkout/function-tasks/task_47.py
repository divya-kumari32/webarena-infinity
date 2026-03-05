import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that quantity selector is enabled on Dawn's 'Product - Gift cards' template."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    dawn = next((t for t in themes if t["name"] == "Dawn"), None)
    if not dawn:
        return False, "Theme 'Dawn' not found."

    templates = state.get("templates", [])
    gift_cards = next(
        (t for t in templates if t["name"] == "Product - Gift cards" and t["themeId"] == dawn["id"]),
        None,
    )
    if not gift_cards:
        return False, "Template 'Product - Gift cards' not found on Dawn theme."

    if gift_cards.get("showQuantitySelector") is not True:
        return False, f"Expected showQuantitySelector to be true on 'Product - Gift cards', got '{gift_cards.get('showQuantitySelector')}'."

    return True, "Quantity selector is enabled on Dawn's 'Product - Gift cards' template."
