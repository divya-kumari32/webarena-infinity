import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that 'Digital Gift Card' product is assigned to 'Product - No checkout buttons' template on Dawn."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    dawn = next((t for t in themes if t["name"] == "Dawn"), None)
    if not dawn:
        return False, "Theme 'Dawn' not found."

    templates = state.get("templates", [])
    template = next(
        (t for t in templates if t["name"] == "Product - No checkout buttons" and t["themeId"] == dawn["id"]),
        None,
    )
    if not template:
        return False, "Template 'Product - No checkout buttons' for Dawn theme not found."

    products = state.get("products", [])
    product = next((p for p in products if p["title"] == "Digital Gift Card"), None)
    if not product:
        return False, "Product 'Digital Gift Card' not found."

    if product.get("templateId") != template["id"]:
        return False, f"Expected 'Digital Gift Card' templateId to be '{template['id']}', got '{product.get('templateId')}'."

    return True, "Product 'Digital Gift Card' is assigned to the 'Product - No checkout buttons' template on Dawn."
