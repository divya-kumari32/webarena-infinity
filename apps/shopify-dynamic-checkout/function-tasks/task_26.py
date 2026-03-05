import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the Sense theme is published (role='main') and Dawn is no longer the main theme."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])

    sense = next((t for t in themes if t["name"] == "Sense"), None)
    if not sense:
        return False, "Theme 'Sense' not found."

    dawn = next((t for t in themes if t["name"] == "Dawn"), None)
    if not dawn:
        return False, "Theme 'Dawn' not found."

    if sense.get("role") != "main":
        return False, f"Expected Sense theme role to be 'main', got '{sense.get('role')}'."

    if dawn.get("role") == "main":
        return False, "Expected Dawn theme to no longer have role 'main', but it still does."

    return True, "Sense theme is published as main and Dawn is no longer the main theme."
