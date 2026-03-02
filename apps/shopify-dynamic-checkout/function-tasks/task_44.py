import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Titanium Watch is assigned to Dawn's 'Product - Gift cards' template."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    dawn = next((t for t in themes if t["name"] == "Dawn"), None)
    if not dawn:
        return False, "Theme 'Dawn' not found."

    templates = state.get("templates", [])
    gift_cards = next(
        (t for t in templates if t["name"] == "Product - Gift cards" and t["themeId"] == dawn["id"]),
        None,
    )
    if not gift_cards:
        return False, "Template 'Product - Gift cards' not found on Dawn theme."

    products = state.get("products", [])
    titanium_watch = next(
        (p for p in products if "Titanium Watch" in p.get("title", "") and "Miyota Movement" in p.get("title", "")),
        None,
    )
    if not titanium_watch:
        return False, "Product 'Titanium Watch \u2013 Miyota Movement' not found."

    if titanium_watch.get("templateId") != gift_cards["id"]:
        return False, f"Expected Titanium Watch templateId to be '{gift_cards['id']}', got '{titanium_watch.get('templateId')}'."

    return True, "Titanium Watch is assigned to Dawn's 'Product - Gift cards' template."
