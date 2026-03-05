import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Dawn's heading scale is 120 and body scale is 90."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    dawn = next((t for t in themes if t["name"] == "Dawn"), None)
    if not dawn:
        return False, "Theme 'Dawn' not found."

    typography = dawn.get("settings", {}).get("typography", {})

    actual_heading = typography.get("headingScale")
    if actual_heading != 120:
        return False, f"Expected headingScale to be 120, got '{actual_heading}'."

    actual_body = typography.get("bodyScale")
    if actual_body != 90:
        return False, f"Expected bodyScale to be 90, got '{actual_body}'."

    return True, "Dawn's heading scale is 120 and body scale is 90."
