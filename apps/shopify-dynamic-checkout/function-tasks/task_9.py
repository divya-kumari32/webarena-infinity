import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Currency Converter Plus app is deactivated."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    installed_apps = state.get("installedApps", [])
    app = next((a for a in installed_apps if a["name"] == "Currency Converter Plus"), None)
    if not app:
        return False, "App 'Currency Converter Plus' not found."

    if app.get("isActive") is not False:
        return False, f"Expected Currency Converter Plus isActive to be false, got '{app.get('isActive')}'."

    return True, "Currency Converter Plus app is deactivated."
