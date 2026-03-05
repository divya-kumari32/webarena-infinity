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

    # Find 'Product - Limited Edition' template on Dawn
    limited_tmpl = next(
        (t for t in templates if t.get("themeId") == dawn_id and t.get("name") == "Product - Limited Edition"),
        None
    )
    if limited_tmpl is None:
        return False, f"Template 'Product - Limited Edition' not found on Dawn (themeId='{dawn_id}')."

    limited_tmpl_id = limited_tmpl.get("id")

    # Check checkout enabled
    if limited_tmpl.get("showAcceleratedCheckout") is not True:
        return False, (
            f"Expected 'Product - Limited Edition' template to have showAcceleratedCheckout=True, "
            f"but got '{limited_tmpl.get('showAcceleratedCheckout')}'."
        )

    # Find Titanium Watch product (title contains 'Titanium Watch')
    titanium_watch = next(
        (p for p in products if "Titanium Watch" in p.get("title", "")),
        None
    )
    if titanium_watch is None:
        return False, "Product containing 'Titanium Watch' not found in state."
    if titanium_watch.get("templateId") != limited_tmpl_id:
        return False, (
            f"Expected '{titanium_watch.get('title')}' to have templateId='{limited_tmpl_id}' "
            f"(Product - Limited Edition), but got '{titanium_watch.get('templateId')}'."
        )

    # Find Silk Blend Scarf product
    silk_scarf = next((p for p in products if p.get("title") == "Silk Blend Scarf"), None)
    if silk_scarf is None:
        return False, "Product 'Silk Blend Scarf' not found in state."
    if silk_scarf.get("templateId") != limited_tmpl_id:
        return False, (
            f"Expected 'Silk Blend Scarf' to have templateId='{limited_tmpl_id}' "
            f"(Product - Limited Edition), but got '{silk_scarf.get('templateId')}'."
        )

    return True, (
        "'Product - Limited Edition' template created on Dawn with checkout enabled, "
        "and Titanium Watch + Silk Blend Scarf assigned to it."
    )
