import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    templates = state.get("templates", [])
    products = state.get("products", [])

    # Find Dawn's Gift cards template
    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found."
    gift_cards_tmpl = next(
        (t for t in templates
         if t.get("themeId") == dawn["id"] and t.get("name") == "Product - Gift cards"),
        None
    )
    if gift_cards_tmpl is None:
        return False, "Template 'Product - Gift cards' not found on Dawn."

    # Check accelerated checkout enabled on Gift cards template
    if gift_cards_tmpl.get("showAcceleratedCheckout") is not True:
        return False, (
            f"Expected 'Product - Gift cards' to have showAcceleratedCheckout=True, "
            f"but got {gift_cards_tmpl.get('showAcceleratedCheckout')}."
        )

    # Check all Atelier Goods products
    atelier_products = [p for p in products if p.get("vendor") == "Atelier Goods"]
    if not atelier_products:
        return False, "No Atelier Goods products found."

    for p in atelier_products:
        # Draft products should now be active
        if p.get("status") == "draft":
            return False, (
                f"Atelier Goods product '{p['title']}' is still in draft status, "
                f"expected it to be activated."
            )

        # All should be on Gift cards template
        if p.get("templateId") != gift_cards_tmpl["id"]:
            return False, (
                f"Atelier Goods product '{p['title']}' has templateId='{p.get('templateId')}', "
                f"expected '{gift_cards_tmpl['id']}' (Product - Gift cards)."
            )

    names = [p["title"] for p in atelier_products]
    return True, (
        f"All Atelier Goods products ({', '.join(names)}) are on 'Product - Gift cards' template "
        f"with checkout enabled. Draft products activated."
    )
