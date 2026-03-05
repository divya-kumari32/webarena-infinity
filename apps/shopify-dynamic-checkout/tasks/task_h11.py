import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    templates = state.get("templates", [])
    products = state.get("products", [])
    cart_attrs = state.get("cartAttributes", [])

    # Find Dawn theme
    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found in state."
    dawn_id = dawn.get("id")

    # Find 'Product - Gift cards' template on Dawn
    gift_cards_tmpl = next(
        (t for t in templates if t.get("themeId") == dawn_id and t.get("name") == "Product - Gift cards"),
        None
    )
    if gift_cards_tmpl is None:
        return False, f"Template 'Product - Gift cards' not found on Dawn (themeId='{dawn_id}')."
    gift_cards_tmpl_id = gift_cards_tmpl.get("id")

    # Find 'Digital Gift Card' product
    gift_card_product = next(
        (p for p in products if p.get("title") == "Digital Gift Card"),
        None
    )
    if gift_card_product is None:
        return False, "Product 'Digital Gift Card' not found in state."

    # Check product is assigned to Gift cards template
    if gift_card_product.get("templateId") != gift_cards_tmpl_id:
        return False, (
            f"Expected 'Digital Gift Card' to have templateId='{gift_cards_tmpl_id}' "
            f"(Product - Gift cards), but got '{gift_card_product.get('templateId')}'."
        )

    # Check Gift cards template has checkout enabled
    if gift_cards_tmpl.get("showAcceleratedCheckout") is not True:
        return False, (
            f"Expected 'Product - Gift cards' template to have showAcceleratedCheckout=True, "
            f"but got '{gift_cards_tmpl.get('showAcceleratedCheckout')}'."
        )

    # Check Terms and conditions cart attribute is active
    terms_attr = next(
        (a for a in cart_attrs if a.get("name") == "Terms and conditions"),
        None
    )
    if terms_attr is None:
        return False, "Cart attribute 'Terms and conditions' not found in state."
    if terms_attr.get("isActive") is not True:
        return False, (
            f"Expected cart attribute 'Terms and conditions' to be active (isActive=True), "
            f"but got isActive={terms_attr.get('isActive')}."
        )

    return True, (
        "Digital Gift Card moved to Gift cards template, checkout enabled on that template, "
        "and Terms and conditions activated."
    )
