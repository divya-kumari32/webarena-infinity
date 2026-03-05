import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Heavyweight Hoodie status is changed to active."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    products = state.get("products", [])

    hoodie = next((p for p in products if "Heavyweight Hoodie" in p.get("title", "")), None)
    if not hoodie:
        return False, "Product 'Heavyweight Hoodie \u2013 Oversized Fit' not found."

    if hoodie.get("status") != "active":
        return False, f"Expected Heavyweight Hoodie status to be 'active', got '{hoodie.get('status')}'."

    return True, "Heavyweight Hoodie status is 'active'."
