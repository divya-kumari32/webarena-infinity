import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that 'Product - No checkout buttons' template is deleted from Dawn and affected products are reassigned to Dawn's default template."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    dawn = next((t for t in themes if t["name"] == "Dawn"), None)
    if not dawn:
        return False, "Theme 'Dawn' not found."

    templates = state.get("templates", [])

    # Check template is deleted
    no_checkout = next(
        (t for t in templates if t["name"] == "Product - No checkout buttons" and t["themeId"] == dawn["id"]),
        None,
    )
    if no_checkout is not None:
        return False, "Template 'Product - No checkout buttons' still exists on Dawn theme."

    # Find Dawn's default template
    dawn_default = next(
        (t for t in templates if t["themeId"] == dawn["id"] and t.get("isDefault") is True),
        None,
    )
    if not dawn_default:
        return False, "Could not find a default template for Dawn theme."

    # Check that products previously using the deleted template are reassigned to Dawn's default
    products = state.get("products", [])
    reassigned_titles = ["Leather Crossbody Bag", "Silk Blend Scarf", "Waxed Canvas Backpack"]

    for title in reassigned_titles:
        product = next((p for p in products if p["title"] == title), None)
        if not product:
            return False, f"Product '{title}' not found."
        if product.get("templateId") != dawn_default["id"]:
            return False, f"Expected '{title}' templateId to be '{dawn_default['id']}' (Dawn default), got '{product.get('templateId')}'."

    return True, "Template 'Product - No checkout buttons' is deleted from Dawn and affected products are reassigned to Dawn's default template."
