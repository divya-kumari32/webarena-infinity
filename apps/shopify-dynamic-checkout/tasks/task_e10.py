import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    products = state.get("products", [])
    beanie = next((p for p in products if "Cashmere Beanie" in p.get("title", "")), None)
    if beanie is None:
        return False, "Product 'Cashmere Beanie' not found in state."

    if beanie.get("status") != "active":
        return False, f"Expected Cashmere Beanie status to be 'active', but got '{beanie.get('status')}'."

    return True, "Cashmere Beanie is marked as active."
