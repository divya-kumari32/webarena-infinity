import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("installedApps", [])

    reconvert = next((a for a in apps if a.get("name") == "ReConvert Upsell & Cross Sell"), None)
    if reconvert is None:
        return False, "App 'ReConvert Upsell & Cross Sell' not found in state."

    if reconvert.get("isActive") is not False:
        return (
            False,
            f"Expected 'ReConvert Upsell & Cross Sell' isActive to be False, "
            f"but got {reconvert.get('isActive')}.",
        )

    privy = next((a for a in apps if a.get("name") == "Privy Pop Ups & Email"), None)
    if privy is None:
        return False, "App 'Privy Pop Ups & Email' not found in state."

    if privy.get("isActive") is not True:
        return (
            False,
            f"Expected 'Privy Pop Ups & Email' isActive to be True, "
            f"but got {privy.get('isActive')}.",
        )

    return True, "ReConvert is disabled and Privy is enabled."
