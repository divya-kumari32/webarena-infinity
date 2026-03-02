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

    # Verify no template named 'Product - No checkout buttons' exists on Dawn
    no_checkout_tmpl = next(
        (t for t in templates if t.get("themeId") == dawn_id and t.get("name") == "Product - No checkout buttons"),
        None
    )
    if no_checkout_tmpl is not None:
        return False, (
            f"Template 'Product - No checkout buttons' still exists on Dawn (id='{no_checkout_tmpl.get('id')}')."
        )

    # Find Dawn's default template
    dawn_default = next(
        (t for t in templates if t.get("themeId") == dawn_id and t.get("isDefault") is True),
        None
    )
    if dawn_default is None:
        return False, "No default template found for Dawn theme."
    dawn_default_id = dawn_default.get("id")

    # Check reassigned products
    reassign_products = ["Leather Crossbody Bag", "Silk Blend Scarf", "Waxed Canvas Backpack"]
    for prod_name in reassign_products:
        product = next((p for p in products if p.get("title") == prod_name), None)
        if product is None:
            return False, f"Product '{prod_name}' not found in state."
        if product.get("templateId") != dawn_default_id:
            return False, (
                f"Expected product '{prod_name}' to have templateId='{dawn_default_id}' "
                f"(Dawn default), but got '{product.get('templateId')}'."
            )

    return True, (
        "'Product - No checkout buttons' template removed from Dawn, and all affected products "
        "reassigned to Dawn's default template."
    )
