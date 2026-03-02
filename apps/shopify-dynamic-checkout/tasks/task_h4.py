import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    templates = state.get("templates", [])
    products = state.get("products", [])

    # Find Dawn theme
    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found in state."
    dawn_id = dawn.get("id")

    # Find 'Product - Premium' template on Dawn
    premium_tmpl = next(
        (t for t in templates if t.get("themeId") == dawn_id and t.get("name") == "Product - Premium"),
        None
    )
    if premium_tmpl is None:
        return False, f"Template 'Product - Premium' not found on Dawn (themeId='{dawn_id}')."

    premium_tmpl_id = premium_tmpl.get("id")

    # Check checkout enabled on Premium template
    if premium_tmpl.get("showAcceleratedCheckout") is not True:
        return False, (
            f"Expected 'Product - Premium' template to have showAcceleratedCheckout=True, "
            f"but got '{premium_tmpl.get('showAcceleratedCheckout')}'."
        )

    # Check all Atelier Goods products are assigned to Premium template
    atelier_products = ["Leather Crossbody Bag", "Silk Blend Scarf", "Cashmere Beanie", "Waxed Canvas Backpack"]
    for prod_name in atelier_products:
        product = next((p for p in products if p.get("title") == prod_name), None)
        if product is None:
            return False, f"Product '{prod_name}' not found in state."
        if product.get("templateId") != premium_tmpl_id:
            return False, (
                f"Expected product '{prod_name}' to have templateId='{premium_tmpl_id}' "
                f"(Product - Premium), but got '{product.get('templateId')}'."
            )

    return True, (
        "'Product - Premium' template created on Dawn with checkout enabled, "
        "and all Atelier Goods products assigned to it."
    )
