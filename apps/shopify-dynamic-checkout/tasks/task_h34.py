import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    templates = state.get("templates", [])
    products = state.get("products", [])

    # Find Dawn theme and templates
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
    dawn_default = next(
        (t for t in templates if t.get("themeId") == dawn["id"] and t.get("isDefault") is True),
        None
    )

    if gift_cards is None:
        return False, "Template 'Product - Gift cards' not found on Dawn."
    if dawn_default is None:
        return False, "Dawn's default template not found."

    # In seed state, products on 'No checkout buttons' template (tmpl_2):
    # prod_15 (Waxed Canvas Backpack, created 2025-04-08) — earliest
    # prod_4 (Leather Crossbody Bag, created 2025-06-01)
    # prod_7 (Silk Blend Scarf, created 2025-09-01) — most recent
    earliest_product = next((p for p in products if p.get("title") == "Waxed Canvas Backpack"), None)
    newest_product = next((p for p in products if p.get("title") == "Silk Blend Scarf"), None)

    if earliest_product is None:
        return False, "Product 'Waxed Canvas Backpack' not found."
    if newest_product is None:
        return False, "Product 'Silk Blend Scarf' not found."

    # Check earliest → Gift cards
    if earliest_product.get("templateId") != gift_cards["id"]:
        return False, (
            f"Expected 'Waxed Canvas Backpack' (earliest, created 2025-04-08) to be on "
            f"'Product - Gift cards' template, but got templateId='{earliest_product.get('templateId')}'."
        )

    # Check newest → default
    if newest_product.get("templateId") != dawn_default["id"]:
        return False, (
            f"Expected 'Silk Blend Scarf' (most recent, created 2025-09-01) to be on "
            f"Dawn's default template, but got templateId='{newest_product.get('templateId')}'."
        )

    return True, (
        "Waxed Canvas Backpack (earliest) moved to 'Gift cards' template, "
        "Silk Blend Scarf (most recent) moved to default template."
    )
