import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    payment_methods = state.get("paymentMethods", [])
    venmo = next((p for p in payment_methods if p.get("name") == "Venmo"), None)
    if venmo is None:
        return False, "Payment method 'Venmo' not found in state."

    if venmo.get("isActive") is not True:
        return False, f"Expected Venmo isActive to be True, but got {venmo.get('isActive')}."

    return True, "Venmo is enabled as a payment method."
