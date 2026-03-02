import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    products = state.get("products", [])
    hoodie = next((p for p in products if "Heavyweight Hoodie" in p.get("title", "")), None)
    if hoodie is None:
        return False, "Product containing 'Heavyweight Hoodie' not found in state."

    if hoodie.get("status") != "active":
        return False, f"Expected Heavyweight Hoodie status to be 'active', but got '{hoodie.get('status')}'."

    return True, "Heavyweight Hoodie has been brought back from archived status and is now active."
