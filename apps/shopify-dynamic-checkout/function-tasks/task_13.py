import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Leather Crossbody Bag is assigned to the Default product template on Dawn."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find the Dawn theme
    themes = state.get("themes", [])
    dawn = next((t for t in themes if t["name"] == "Dawn"), None)
    if not dawn:
        return False, "Theme 'Dawn' not found."

    # Find the Default product template for Dawn
    templates = state.get("templates", [])
    default_template = next(
        (t for t in templates if t["name"] == "Default product" and t["themeId"] == dawn["id"]),
        None,
    )
    if not default_template:
        return False, "Template 'Default product' for Dawn theme not found."

    # Find the product
    products = state.get("products", [])
    product = next((p for p in products if p["title"] == "Leather Crossbody Bag"), None)
    if not product:
        return False, "Product 'Leather Crossbody Bag' not found."

    if product.get("templateId") != default_template["id"]:
        return False, f"Expected Leather Crossbody Bag templateId to be '{default_template['id']}', got '{product.get('templateId')}'."

    return True, "Leather Crossbody Bag is assigned to the Default product template."
