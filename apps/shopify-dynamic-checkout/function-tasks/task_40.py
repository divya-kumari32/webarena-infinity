import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the 'Privy Pop Ups & Email' app is activated."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("installedApps", [])
    privy = next((a for a in apps if a["name"] == "Privy Pop Ups & Email"), None)
    if not privy:
        return False, "App 'Privy Pop Ups & Email' not found."

    if privy.get("isActive") is not True:
        return False, f"Expected 'Privy Pop Ups & Email' isActive to be true, got '{privy.get('isActive')}'."

    return True, "App 'Privy Pop Ups & Email' is activated."
