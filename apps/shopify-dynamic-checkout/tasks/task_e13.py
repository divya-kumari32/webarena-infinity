import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    installed_apps = state.get("installedApps", [])
    oberlo = next((a for a in installed_apps if a.get("name") == "Oberlo Dropshipping"), None)
    if oberlo is None:
        return False, "Installed app 'Oberlo Dropshipping' not found in state."

    if oberlo.get("isActive") is not False:
        return False, f"Expected Oberlo Dropshipping isActive to be False, but got {oberlo.get('isActive')}."

    return True, "Oberlo Dropshipping is disabled."
