import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    cart_attributes = state.get("cartAttributes", [])
    terms = next((a for a in cart_attributes if a.get("name") == "Terms and conditions"), None)
    if terms is None:
        return False, "Cart attribute 'Terms and conditions' not found in state."

    if terms.get("isActive") is not True:
        return False, f"Expected Terms and conditions isActive to be True, but got {terms.get('isActive')}."

    return True, "Terms and conditions are required before checkout."
