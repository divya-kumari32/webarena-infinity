import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that 'Terms & conditions' is enabled and 'Gift wrapping' is disabled."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    cart_attributes = state.get("cartAttributes", [])

    terms = next((ca for ca in cart_attributes if ca["name"] == "Terms and conditions"), None)
    if not terms:
        return False, "Cart attribute 'Terms and conditions' not found."

    gift_wrapping = next((ca for ca in cart_attributes if ca["name"] == "Gift wrapping"), None)
    if not gift_wrapping:
        return False, "Cart attribute 'Gift wrapping' not found."

    if terms.get("isActive") is not True:
        return False, f"Expected Terms & conditions isActive to be true, got '{terms.get('isActive')}'."

    if gift_wrapping.get("isActive") is not False:
        return False, f"Expected Gift wrapping isActive to be false, got '{gift_wrapping.get('isActive')}'."

    return True, "'Terms & conditions' is enabled and 'Gift wrapping' is disabled."
