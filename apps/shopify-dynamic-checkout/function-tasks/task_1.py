import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the 'Craft' theme is published (role='main') and 'Dawn' is no longer the main theme."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])

    craft = next((t for t in themes if t["name"] == "Craft"), None)
    if not craft:
        return False, "Theme 'Craft' not found."

    dawn = next((t for t in themes if t["name"] == "Dawn"), None)
    if not dawn:
        return False, "Theme 'Dawn' not found."

    if craft.get("role") != "main":
        return False, f"Expected Craft theme role to be 'main', got '{craft.get('role')}'."

    if dawn.get("role") == "main":
        return False, f"Expected Dawn theme to no longer have role 'main', but it still does."

    return True, "Craft theme is published as main and Dawn is no longer the main theme."
