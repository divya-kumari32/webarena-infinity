import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Venmo is activated."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    payment_methods = state.get("paymentMethods", [])

    venmo = next((pm for pm in payment_methods if pm["name"] == "Venmo"), None)
    if not venmo:
        return False, "Payment method 'Venmo' not found."

    if venmo.get("isActive") is not True:
        return False, f"Expected Venmo isActive to be true, got '{venmo.get('isActive')}'."

    return True, "Venmo is activated."
