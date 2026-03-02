import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the quantity selector is disabled on Dawn's Default product template."""
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
        (t for t in templates if t["name"] == "Default product" and t["themeId"] == dawn["id"]),
        None,
    )
    if not template:
        return False, "Template 'Default product' for Dawn theme not found."

    if template.get("showQuantitySelector") is not False:
        return False, f"Expected showQuantitySelector to be false, got '{template.get('showQuantitySelector')}'."

    return True, "Quantity selector is disabled on Dawn's Default product template."
