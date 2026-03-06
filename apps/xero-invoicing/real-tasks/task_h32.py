import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    themes = state.get("brandingThemes", [])

    gov_theme = next((t for t in themes if t["name"] == "Government"), None)
    if not gov_theme:
        return False, "Branding theme 'Government' not found."

    if not gov_theme.get("isDefault"):
        return False, "Government theme is not set as default."

    # Ensure no other theme is also default
    other_defaults = [t for t in themes if t["isDefault"] and t["name"] != "Government"]
    if other_defaults:
        return False, f"Multiple default themes found: Government and {other_defaults[0]['name']}."

    return True, "Government branding theme created and set as default."
