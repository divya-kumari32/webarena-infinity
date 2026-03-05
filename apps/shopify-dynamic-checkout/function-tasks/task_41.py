import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the 'Ride' theme is published (role='main') and Dawn is no longer 'main'."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])

    ride = next((t for t in themes if t["name"] == "Ride"), None)
    if not ride:
        return False, "Theme 'Ride' not found."

    dawn = next((t for t in themes if t["name"] == "Dawn"), None)
    if not dawn:
        return False, "Theme 'Dawn' not found."

    if ride.get("role") != "main":
        return False, f"Expected Ride theme role to be 'main', got '{ride.get('role')}'."

    if dawn.get("role") == "main":
        return False, "Expected Dawn theme to no longer have role 'main', but it still does."

    return True, "Ride theme is published as main and Dawn is no longer the main theme."
