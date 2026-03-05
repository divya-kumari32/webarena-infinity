import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the Terms and conditions cart attribute is enabled."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    cart_attributes = state.get("cartAttributes", [])
    terms = next((c for c in cart_attributes if c["name"] == "Terms and conditions"), None)
    if not terms:
        return False, "Cart attribute 'Terms and conditions' not found."

    if terms.get("isActive") is not True:
        return False, f"Expected Terms and conditions isActive to be true, got '{terms.get('isActive')}'."

    return True, "Terms and conditions cart attribute is enabled."
