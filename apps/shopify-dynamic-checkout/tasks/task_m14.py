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
        (t for t in templates if t.get("themeId") == dawn_id and t.get("isDefault") is True),
        None,
    )
    if default_tmpl is None:
        return False, f"Default product template not found for Dawn theme (id={dawn_id})."
    default_tmpl_id = default_tmpl.get("id")

    products = state.get("products", [])

    backpack = next((p for p in products if p.get("title") == "Waxed Canvas Backpack"), None)
    if backpack is None:
        return False, "Product 'Waxed Canvas Backpack' not found in state."

    if backpack.get("templateId") != default_tmpl_id:
        return (
            False,
            f"Expected Waxed Canvas Backpack templateId to be '{default_tmpl_id}' (Dawn default), "
            f"but got '{backpack.get('templateId')}'.",
        )

    scarf = next((p for p in products if p.get("title") == "Silk Blend Scarf"), None)
    if scarf is None:
        return False, "Product 'Silk Blend Scarf' not found in state."

    if scarf.get("templateId") != default_tmpl_id:
        return (
            False,
            f"Expected Silk Blend Scarf templateId to be '{default_tmpl_id}' (Dawn default), "
            f"but got '{scarf.get('templateId')}'.",
        )

    return True, "Waxed Canvas Backpack and Silk Blend Scarf are both assigned to Dawn's default template."
