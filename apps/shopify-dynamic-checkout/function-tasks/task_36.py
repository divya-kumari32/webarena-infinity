import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Dawn's accent button text color is '#000000'."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    dawn = next((t for t in themes if t["name"] == "Dawn"), None)
    if not dawn:
        return False, "Theme 'Dawn' not found."

    accent_button_text = dawn.get("settings", {}).get("colors", {}).get("accentButtonText")
    if accent_button_text != "#000000":
        return False, f"Expected Dawn accentButtonText to be '#000000', got '{accent_button_text}'."

    return True, "Dawn's accent button text color is set to '#000000'."
