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
    seasonal_tmpl = next(
        (t for t in templates if t.get("themeId") == dawn_id and t.get("name") == "Product - Seasonal"),
        None,
    )
    if seasonal_tmpl is None:
        return False, f"Template 'Product - Seasonal' not found for Dawn theme (id={dawn_id})."

    if seasonal_tmpl.get("isAlternate") is not True:
        return (
            False,
            f"Expected 'Product - Seasonal' template isAlternate to be True, "
            f"but got {seasonal_tmpl.get('isAlternate')}.",
        )

    return True, "Alternate template 'Product - Seasonal' exists on Dawn and is marked as alternate."
