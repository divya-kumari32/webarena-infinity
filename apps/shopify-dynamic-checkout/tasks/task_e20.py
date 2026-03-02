import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    installed_apps = state.get("installedApps", [])
    carthook = next((a for a in installed_apps if "CartHook" in a.get("name", "")), None)
    if carthook is None:
        return False, "Installed app containing 'CartHook' not found in state."

    if carthook.get("isActive") is not True:
        return False, f"Expected CartHook app isActive to be True, but got {carthook.get('isActive')}."

    return True, "CartHook Post Purchase Offers app is activated."
