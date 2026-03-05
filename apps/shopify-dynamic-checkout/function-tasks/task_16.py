import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that 'Product - Gift cards' template is deleted from Dawn and affected products reassigned."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    dawn = next((t for t in themes if t["name"] == "Dawn"), None)
    if not dawn:
        return False, "Theme 'Dawn' not found."

    templates = state.get("templates", [])

    # Check that 'Product - Gift cards' no longer exists for Dawn
    gift_cards_tmpl = next(
        (t for t in templates if t["name"] == "Product - Gift cards" and t["themeId"] == dawn["id"]),
        None,
    )
    if gift_cards_tmpl is not None:
        return False, "Template 'Product - Gift cards' still exists for Dawn theme."

    # Find Dawn's default template
    dawn_default = next(
        (t for t in templates if t["themeId"] == dawn["id"] and t.get("isDefault") is True),
        None,
    )
    if not dawn_default:
        return False, "Could not find Dawn's default template."

    # Check that Digital Gift Card product now uses Dawn's default template
    products = state.get("products", [])
    gift_card_product = next(
        (p for p in products if p["title"] == "Digital Gift Card"),
        None,
    )
    if not gift_card_product:
        return False, "Product 'Digital Gift Card' not found."

    if gift_card_product.get("templateId") != dawn_default["id"]:
        return False, (
            f"Expected Digital Gift Card templateId to be '{dawn_default['id']}' "
            f"(Dawn's default), got '{gift_card_product.get('templateId')}'."
        )

    return True, "Template 'Product - Gift cards' deleted and Digital Gift Card reassigned to Dawn's default template."
