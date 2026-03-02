import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Dawn's accent color is changed to '#E11D48'."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    dawn = next((t for t in themes if t["name"] == "Dawn"), None)
    if not dawn:
        return False, "Theme 'Dawn' not found."

    accent_color = dawn.get("settings", {}).get("colors", {}).get("accentColor")
    if accent_color != "#E11D48":
        return False, f"Expected Dawn accent color to be '#E11D48', got '{accent_color}'."

    return True, "Dawn's accent color is set to '#E11D48'."
