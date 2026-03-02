import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    craft = next((t for t in themes if t.get("name") == "Craft"), None)
    if craft is None:
        return False, "Theme 'Craft' not found in state."
    craft_id = craft.get("id")

    templates = state.get("templates", [])
    express_tmpl = next(
        (t for t in templates if t.get("themeId") == craft_id and t.get("name") == "Product - Express"),
        None,
    )
    if express_tmpl is None:
        return False, f"Template 'Product - Express' not found for Craft theme (id={craft_id})."

    if express_tmpl.get("isAlternate") is not True:
        return (
            False,
            f"Expected 'Product - Express' template isAlternate to be True, "
            f"but got {express_tmpl.get('isAlternate')}.",
        )

    return True, "Alternate template 'Product - Express' exists on Craft and is marked as alternate."
