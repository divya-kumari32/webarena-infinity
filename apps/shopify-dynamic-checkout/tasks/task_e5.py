import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    installed_apps = state.get("installedApps", [])
    currency_converter = next(
        (a for a in installed_apps if a.get("name") == "Currency Converter Plus"), None
    )
    if currency_converter is None:
        return False, "Installed app 'Currency Converter Plus' not found in state."

    if currency_converter.get("isActive") is not False:
        return (
            False,
            f"Expected Currency Converter Plus isActive to be False, but got {currency_converter.get('isActive')}.",
        )

    return True, "Currency Converter Plus app is disabled."
