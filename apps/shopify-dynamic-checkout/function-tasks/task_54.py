import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Silk Blend Scarf is assigned to Dawn's 'Default product' template."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    dawn = next((t for t in themes if t["name"] == "Dawn"), None)
    if not dawn:
        return False, "Theme 'Dawn' not found."

    templates = state.get("templates", [])
    default_product = next(
        (t for t in templates if t["name"] == "Default product" and t["themeId"] == dawn["id"]),
        None,
    )
    if not default_product:
        return False, "Template 'Default product' not found on Dawn theme."

    products = state.get("products", [])
    silk_scarf = next((p for p in products if "Silk Blend Scarf" in p.get("title", "")), None)
    if not silk_scarf:
        return False, "Product 'Silk Blend Scarf' not found."

    if silk_scarf.get("templateId") != default_product["id"]:
        return False, f"Expected Silk Blend Scarf templateId to be '{default_product['id']}', got '{silk_scarf.get('templateId')}'."

    return True, "Silk Blend Scarf is assigned to Dawn's 'Default product' template."
