import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    products = state.get("products", [])
    themes = state.get("themes", [])
    templates = state.get("templates", [])

    # Find Dawn's default template
    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found."
    dawn_default = next(
        (t for t in templates if t.get("themeId") == dawn["id"] and t.get("isDefault") is True),
        None
    )
    if dawn_default is None:
        return False, "Dawn's default template not found."

    # Check all products with compare-at prices are archived
    compare_at_products = []
    for p in products:
        has_compare_at = any(
            v.get("compareAtPrice") is not None
            for v in p.get("variants", [])
        )
        if has_compare_at:
            compare_at_products.append(p)
            if p.get("status") != "archived":
                return False, (
                    f"Product '{p['title']}' has compare-at prices but status is "
                    f"'{p.get('status')}', expected 'archived'."
                )

    if not compare_at_products:
        return False, "No products with compare-at prices found."

    # Check remaining active Atelier Goods products are on default template
    atelier_products = [
        p for p in products
        if p.get("vendor") == "Atelier Goods"
        and p.get("status") == "active"
    ]
    for p in atelier_products:
        if p.get("templateId") != dawn_default["id"]:
            return False, (
                f"Active Atelier Goods product '{p['title']}' has templateId='{p.get('templateId')}', "
                f"expected '{dawn_default['id']}' (Dawn default)."
            )

    archived_names = [p["title"] for p in compare_at_products]
    atelier_names = [p["title"] for p in atelier_products]
    return True, (
        f"Products with compare-at prices archived: {', '.join(archived_names)}. "
        f"Active Atelier Goods products on Dawn default: {', '.join(atelier_names)}."
    )
