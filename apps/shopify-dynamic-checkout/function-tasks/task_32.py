import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the 'Oberlo Dropshipping' app is deactivated."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("installedApps", [])
    oberlo = next((a for a in apps if a["name"] == "Oberlo Dropshipping"), None)
    if not oberlo:
        return False, "App 'Oberlo Dropshipping' not found."

    if oberlo.get("isActive") is not False:
        return False, f"Expected 'Oberlo Dropshipping' isActive to be false, got '{oberlo.get('isActive')}'."

    return True, "App 'Oberlo Dropshipping' is deactivated."
