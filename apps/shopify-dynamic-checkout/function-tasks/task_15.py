import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that a new alternate template 'Product - Premium' exists on Dawn."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    dawn = next((t for t in themes if t["name"] == "Dawn"), None)
    if not dawn:
        return False, "Theme 'Dawn' not found."

    templates = state.get("templates", [])
    premium = next(
        (t for t in templates if t["name"] == "Product - Premium" and t["themeId"] == dawn["id"]),
        None,
    )
    if not premium:
        return False, "Template 'Product - Premium' not found for Dawn theme."

    if premium.get("isDefault") is not False:
        return False, f"Expected isDefault to be false, got '{premium.get('isDefault')}'."

    if premium.get("isAlternate") is not True:
        return False, f"Expected isAlternate to be true, got '{premium.get('isAlternate')}'."

    return True, "Alternate template 'Product - Premium' exists on Dawn with correct flags."
