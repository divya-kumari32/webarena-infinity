import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the Gift wrapping cart attribute is disabled."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    cart_attributes = state.get("cartAttributes", [])
    gift_wrapping = next((c for c in cart_attributes if c["name"] == "Gift wrapping"), None)
    if not gift_wrapping:
        return False, "Cart attribute 'Gift wrapping' not found."

    if gift_wrapping.get("isActive") is not False:
        return False, f"Expected Gift wrapping isActive to be false, got '{gift_wrapping.get('isActive')}'."

    return True, "Gift wrapping cart attribute is disabled."
