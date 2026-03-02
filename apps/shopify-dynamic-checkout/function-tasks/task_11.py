import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Cashmere Beanie product status is changed to active."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    products = state.get("products", [])
    product = next((p for p in products if p["title"] == "Cashmere Beanie"), None)
    if not product:
        return False, "Product 'Cashmere Beanie' not found."

    if product.get("status") != "active":
        return False, f"Expected Cashmere Beanie status to be 'active', got '{product.get('status')}'."

    return True, "Cashmere Beanie product status is active."
