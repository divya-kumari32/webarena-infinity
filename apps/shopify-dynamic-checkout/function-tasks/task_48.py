import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that both 'Gift wrapping' and 'Delivery date' cart attributes are disabled."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    cart_attributes = state.get("cartAttributes", [])

    gift_wrapping = next((ca for ca in cart_attributes if ca["name"] == "Gift wrapping"), None)
    if not gift_wrapping:
        return False, "Cart attribute 'Gift wrapping' not found."

    delivery_date = next((ca for ca in cart_attributes if ca["name"] == "Delivery date"), None)
    if not delivery_date:
        return False, "Cart attribute 'Delivery date' not found."

    if gift_wrapping.get("isActive") is not False:
        return False, f"Expected Gift wrapping isActive to be false, got '{gift_wrapping.get('isActive')}'."

    if delivery_date.get("isActive") is not False:
        return False, f"Expected Delivery date isActive to be false, got '{delivery_date.get('isActive')}'."

    return True, "Both 'Gift wrapping' and 'Delivery date' cart attributes are disabled."
