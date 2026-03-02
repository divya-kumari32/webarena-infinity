import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Canvas Sneakers is assigned to the Product - No checkout buttons template on Dawn."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find the Dawn theme
    themes = state.get("themes", [])
    dawn = next((t for t in themes if t["name"] == "Dawn"), None)
    if not dawn:
        return False, "Theme 'Dawn' not found."

    # Find the Product - No checkout buttons template for Dawn
    templates = state.get("templates", [])
    no_checkout_template = next(
        (t for t in templates if t["name"] == "Product - No checkout buttons" and t["themeId"] == dawn["id"]),
        None,
    )
    if not no_checkout_template:
        return False, "Template 'Product - No checkout buttons' for Dawn theme not found."

    # Find the product
    products = state.get("products", [])
    product = next((p for p in products if p["title"] == "Canvas Sneakers"), None)
    if not product:
        return False, "Product 'Canvas Sneakers' not found."

    if product.get("templateId") != no_checkout_template["id"]:
        return False, f"Expected Canvas Sneakers templateId to be '{no_checkout_template['id']}', got '{product.get('templateId')}'."

    return True, "Canvas Sneakers is assigned to the Product - No checkout buttons template."
