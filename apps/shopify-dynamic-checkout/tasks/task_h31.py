import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    products = state.get("products", [])
    themes = state.get("themes", [])
    templates = state.get("templates", [])

    # Find the product with gift card recipient fields
    gift_card_products = [p for p in products if p.get("hasGiftCardRecipientFields") is True]
    if not gift_card_products:
        return False, "No product with gift card recipient fields found."
    if len(gift_card_products) != 1:
        return False, f"Expected exactly 1 product with gift card fields, found {len(gift_card_products)}."

    gc_product = gift_card_products[0]

    # Find Dawn's default template
    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found."
    dawn_default = next(
        (t for t in templates if t.get("themeId") == dawn["id"] and t.get("isDefault") is True),
        None
    )
    if dawn_default is None:
        return False, "Dawn's default template not found."

    # Check product is on default template
    if gc_product.get("templateId") != dawn_default["id"]:
        return False, (
            f"Expected '{gc_product['title']}' (gift card product) to be on "
            f"Dawn's default template ('{dawn_default['id']}'), "
            f"but got templateId='{gc_product.get('templateId')}'."
        )

    # Check accelerated checkout is disabled on default template
    if dawn_default.get("showAcceleratedCheckout") is not False:
        return False, (
            f"Expected Dawn's default template to have showAcceleratedCheckout=False, "
            f"but got {dawn_default.get('showAcceleratedCheckout')}."
        )

    return True, (
        f"'{gc_product['title']}' (only product with gift card fields) moved to "
        f"Dawn's default template, and accelerated checkout disabled on that template."
    )
