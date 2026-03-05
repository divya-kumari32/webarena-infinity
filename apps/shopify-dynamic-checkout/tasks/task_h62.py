import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Move Activewear→No checkout, Outerwear→Gift cards, enable checkout on both."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    templates = state.get("templates", [])
    products = state.get("products", [])

    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found."

    no_checkout = next(
        (t for t in templates
         if t.get("themeId") == dawn["id"] and t.get("name") == "Product - No checkout buttons"),
        None
    )
    gift_cards = next(
        (t for t in templates
         if t.get("themeId") == dawn["id"] and t.get("name") == "Product - Gift cards"),
        None
    )
    if no_checkout is None:
        return False, "Template 'Product - No checkout buttons' not found on Dawn."
    if gift_cards is None:
        return False, "Template 'Product - Gift cards' not found on Dawn."

    # Check Activewear products are on No checkout buttons template
    activewear = [p for p in products if p.get("productType") == "Activewear"]
    for p in activewear:
        if p.get("templateId") != no_checkout["id"]:
            return False, (f"Expected Activewear product '{p['title']}' on 'No checkout buttons' "
                          f"template, but it's on template '{p.get('templateId')}'.")

    # Check Outerwear products are on Gift cards template
    outerwear = [p for p in products if p.get("productType") == "Outerwear"]
    for p in outerwear:
        if p.get("templateId") != gift_cards["id"]:
            return False, (f"Expected Outerwear product '{p['title']}' on 'Gift cards' "
                          f"template, but it's on template '{p.get('templateId')}'.")

    # Check accelerated checkout enabled on both templates
    if no_checkout.get("showAcceleratedCheckout") is not True:
        return False, (f"Expected 'No checkout buttons' to have checkout enabled, "
                      f"got {no_checkout.get('showAcceleratedCheckout')}.")
    if gift_cards.get("showAcceleratedCheckout") is not True:
        return False, (f"Expected 'Gift cards' to have checkout enabled, "
                      f"got {gift_cards.get('showAcceleratedCheckout')}.")

    return True, (f"{len(activewear)} Activewear products moved to 'No checkout buttons', "
                  f"{len(outerwear)} Outerwear products moved to 'Gift cards'. "
                  f"Checkout enabled on both templates.")
