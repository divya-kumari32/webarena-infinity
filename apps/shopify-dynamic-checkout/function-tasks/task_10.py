import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that CartHook app is activated."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    installed_apps = state.get("installedApps", [])
    app = next((a for a in installed_apps if "CartHook" in a["name"]), None)
    if not app:
        return False, "App 'CartHook Post Purchase Offers' not found."

    if app.get("isActive") is not True:
        return False, f"Expected CartHook Post Purchase Offers isActive to be true, got '{app.get('isActive')}'."

    return True, "CartHook Post Purchase Offers app is activated."
