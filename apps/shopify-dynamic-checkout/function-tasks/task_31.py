import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the 'Delivery date' cart attribute is disabled."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    cart_attributes = state.get("cartAttributes", [])
    delivery_date = next((a for a in cart_attributes if a["name"] == "Delivery date"), None)
    if not delivery_date:
        return False, "Cart attribute 'Delivery date' not found."

    if delivery_date.get("isActive") is not False:
        return False, f"Expected 'Delivery date' isActive to be false, got '{delivery_date.get('isActive')}'."

    return True, "Cart attribute 'Delivery date' is disabled."
