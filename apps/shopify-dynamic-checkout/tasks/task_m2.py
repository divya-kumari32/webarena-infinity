import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found in state."
    dawn_id = dawn.get("id")

    templates = state.get("templates", [])
    default_tmpl = next(
        (t for t in templates if t.get("themeId") == dawn_id and t.get("name") == "Default product" and t.get("isDefault") is True),
        None,
    )
    if default_tmpl is None:
        return False, f"Default product template not found for Dawn theme (id={dawn_id})."
    default_tmpl_id = default_tmpl.get("id")

    products = state.get("products", [])
    product = next((p for p in products if p.get("title") == "Leather Crossbody Bag"), None)
    if product is None:
        return False, "Product 'Leather Crossbody Bag' not found in state."

    if product.get("templateId") != default_tmpl_id:
        return (
            False,
            f"Expected Leather Crossbody Bag templateId to be '{default_tmpl_id}' (Dawn default), "
            f"but got '{product.get('templateId')}'.",
        )

    return True, "Leather Crossbody Bag is assigned to Dawn's default product template."
