import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Apple Pay is deactivated."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    payment_methods = state.get("paymentMethods", [])
    apple_pay = next((pm for pm in payment_methods if pm["name"] == "Apple Pay"), None)
    if not apple_pay:
        return False, "Payment method 'Apple Pay' not found."

    if apple_pay.get("isActive") is not False:
        return False, f"Expected Apple Pay isActive to be false, got '{apple_pay.get('isActive')}'."

    return True, "Apple Pay has been deactivated."
