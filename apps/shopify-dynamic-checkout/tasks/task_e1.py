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
    if craft.get("role") != "main":
        return False, f"Expected Craft theme role to be 'main', but got '{craft.get('role')}'."

    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found in state."
    if dawn.get("role") == "main":
        return False, "Dawn theme still has role 'main'; it should no longer be the live theme."

    return True, "Craft is now the live theme and Dawn is no longer the live theme."
