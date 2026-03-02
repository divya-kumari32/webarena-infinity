import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that both PayPal and Google Pay are deactivated."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    payment_methods = state.get("paymentMethods", [])

    paypal = next((pm for pm in payment_methods if pm["name"] == "PayPal"), None)
    if not paypal:
        return False, "Payment method 'PayPal' not found."

    google_pay = next((pm for pm in payment_methods if pm["name"] == "Google Pay"), None)
    if not google_pay:
        return False, "Payment method 'Google Pay' not found."

    if paypal.get("isActive") is not False:
        return False, f"Expected PayPal isActive to be false, got '{paypal.get('isActive')}'."

    if google_pay.get("isActive") is not False:
        return False, f"Expected Google Pay isActive to be false, got '{google_pay.get('isActive')}'."

    return True, "Both PayPal and Google Pay are deactivated."
