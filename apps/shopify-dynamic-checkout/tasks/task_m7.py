import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("installedApps", [])

    currency_converter = next((a for a in apps if a.get("name") == "Currency Converter Plus"), None)
    if currency_converter is None:
        return False, "App 'Currency Converter Plus' not found in state."

    if currency_converter.get("isActive") is not False:
        return (
            False,
            f"Expected 'Currency Converter Plus' isActive to be False, "
            f"but got {currency_converter.get('isActive')}.",
        )

    oberlo = next((a for a in apps if a.get("name") == "Oberlo Dropshipping"), None)
    if oberlo is None:
        return False, "App 'Oberlo Dropshipping' not found in state."

    if oberlo.get("isActive") is not False:
        return (
            False,
            f"Expected 'Oberlo Dropshipping' isActive to be False, "
            f"but got {oberlo.get('isActive')}.",
        )

    reconvert = next((a for a in apps if a.get("name") == "ReConvert Upsell & Cross Sell"), None)
    if reconvert is None:
        return False, "App 'ReConvert Upsell & Cross Sell' not found in state."

    if reconvert.get("isActive") is not False:
        return (
            False,
            f"Expected 'ReConvert Upsell & Cross Sell' isActive to be False, "
            f"but got {reconvert.get('isActive')}.",
        )

    return True, "All apps with checkout conflicts (Currency Converter Plus, Oberlo Dropshipping, ReConvert Upsell & Cross Sell) are deactivated."
