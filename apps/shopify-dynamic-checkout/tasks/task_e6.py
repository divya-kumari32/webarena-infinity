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
    default_product = next(
        (t for t in templates if t.get("themeId") == dawn_id and t.get("name") == "Default product"),
        None,
    )
    if default_product is None:
        return False, f"Template 'Default product' not found for Dawn theme (id={dawn_id})."

    if default_product.get("showQuantitySelector") is not False:
        return (
            False,
            f"Expected showQuantitySelector to be False on Dawn's Default product template, "
            f"but got {default_product.get('showQuantitySelector')}.",
        )

    return True, "Quantity selector is removed from Dawn's Default product template."
