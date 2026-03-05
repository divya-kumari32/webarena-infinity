import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Two compare-at products: higher price→Gift cards, lower→No checkout. Enable both."""
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
        return False, "Template 'Product - No checkout buttons' not found."
    if gift_cards is None:
        return False, "Template 'Product - Gift cards' not found."

    # Seed data: Merino Wool Sweater ($89.99 compare-at), Linen Blend Blazer ($139.99 compare-at)
    # Higher price = Blazer → Gift cards, Lower price = Sweater → No checkout
    sweater = next((p for p in products if p.get("title") == "Merino Wool Sweater"), None)
    blazer = next((p for p in products if p.get("title") == "Linen Blend Blazer"), None)

    if sweater is None:
        return False, "Merino Wool Sweater not found."
    if blazer is None:
        return False, "Linen Blend Blazer not found."

    # Check Blazer (higher price) on Gift cards
    if blazer.get("templateId") != gift_cards["id"]:
        return False, (f"Expected Linen Blend Blazer (higher price) on 'Gift cards', "
                      f"but it's on template '{blazer.get('templateId')}'.")

    # Check Sweater (lower price) on No checkout
    if sweater.get("templateId") != no_checkout["id"]:
        return False, (f"Expected Merino Wool Sweater (lower price) on 'No checkout buttons', "
                      f"but it's on template '{sweater.get('templateId')}'.")

    # Check checkout enabled on both
    if no_checkout.get("showAcceleratedCheckout") is not True:
        return False, (f"Expected 'No checkout buttons' checkout enabled, "
                      f"got {no_checkout.get('showAcceleratedCheckout')}.")
    if gift_cards.get("showAcceleratedCheckout") is not True:
        return False, (f"Expected 'Gift cards' checkout enabled, "
                      f"got {gift_cards.get('showAcceleratedCheckout')}.")

    return True, ("Blazer ($139.99) on 'Gift cards', Sweater ($89.99) on 'No checkout buttons'. "
                  "Checkout enabled on both templates.")
