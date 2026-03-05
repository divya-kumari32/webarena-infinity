import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that both 'Currency Converter Plus' and 'ReConvert' apps are deactivated."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("installedApps", [])

    currency_converter = next((a for a in apps if a["name"] == "Currency Converter Plus"), None)
    if not currency_converter:
        return False, "App 'Currency Converter Plus' not found."

    reconvert = next((a for a in apps if "ReConvert" in a["name"]), None)
    if not reconvert:
        return False, "App 'ReConvert Upsell & Cross Sell' not found."

    if currency_converter.get("isActive") is not False:
        return False, f"Expected Currency Converter Plus isActive to be false, got '{currency_converter.get('isActive')}'."

    if reconvert.get("isActive") is not False:
        return False, f"Expected ReConvert isActive to be false, got '{reconvert.get('isActive')}'."

    return True, "Both 'Currency Converter Plus' and 'ReConvert' apps are deactivated."
