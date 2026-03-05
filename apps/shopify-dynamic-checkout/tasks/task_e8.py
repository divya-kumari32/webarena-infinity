import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    cart_attributes = state.get("cartAttributes", [])
    delivery_date = next((a for a in cart_attributes if a.get("name") == "Delivery date"), None)
    if delivery_date is None:
        return False, "Cart attribute 'Delivery date' not found in state."

    if delivery_date.get("isActive") is not False:
        return False, f"Expected Delivery date isActive to be False, but got {delivery_date.get('isActive')}."

    return True, "Delivery date picker is disabled in the cart."
