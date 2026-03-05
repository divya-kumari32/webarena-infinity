import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found in state."
    dawn_id = dawn.get("id")

    templates = state.get("templates", [])

    # Verify the Gift cards template no longer exists
    gift_cards_tmpl = next(
        (t for t in templates if t.get("themeId") == dawn_id and t.get("name") == "Product - Gift cards"),
        None,
    )
    if gift_cards_tmpl is not None:
        return False, "Template 'Product - Gift cards' still exists on Dawn; it should have been deleted."

    # Verify Digital Gift Card product was reassigned to Dawn's default template
    products = state.get("products", [])
    gift_card_product = next((p for p in products if p.get("title") == "Digital Gift Card"), None)
    if gift_card_product is None:
        return False, "Product 'Digital Gift Card' not found in state."

    default_tmpl = next(
        (t for t in templates if t.get("themeId") == dawn_id and t.get("isDefault") is True),
        None,
    )
    if default_tmpl is None:
        return False, f"Default product template not found for Dawn theme (id={dawn_id})."
    default_tmpl_id = default_tmpl.get("id")

    if gift_card_product.get("templateId") != default_tmpl_id:
        return (
            False,
            f"Expected Digital Gift Card templateId to be '{default_tmpl_id}' (Dawn default), "
            f"but got '{gift_card_product.get('templateId')}'.",
        )

    return True, "Template 'Product - Gift cards' deleted from Dawn and Digital Gift Card reassigned to default template."
