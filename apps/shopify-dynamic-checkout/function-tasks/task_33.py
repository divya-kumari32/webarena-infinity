import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the 'ReConvert Upsell & Cross Sell' app is deactivated."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("installedApps", [])
    reconvert = next((a for a in apps if a["name"] == "ReConvert Upsell & Cross Sell"), None)
    if not reconvert:
        return False, "App 'ReConvert Upsell & Cross Sell' not found."

    if reconvert.get("isActive") is not False:
        return False, f"Expected 'ReConvert Upsell & Cross Sell' isActive to be false, got '{reconvert.get('isActive')}'."

    return True, "App 'ReConvert Upsell & Cross Sell' is deactivated."
