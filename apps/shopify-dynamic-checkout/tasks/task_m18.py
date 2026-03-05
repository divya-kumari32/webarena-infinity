import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    payment_methods = state.get("paymentMethods", [])

    paypal = next((pm for pm in payment_methods if pm.get("name") == "PayPal"), None)
    if paypal is None:
        return False, "Payment method 'PayPal' not found in state."

    if paypal.get("isActive") is not False:
        return (
            False,
            f"Expected PayPal isActive to be False, but got {paypal.get('isActive')}.",
        )

    google_pay = next((pm for pm in payment_methods if pm.get("name") == "Google Pay"), None)
    if google_pay is None:
        return False, "Payment method 'Google Pay' not found in state."

    if google_pay.get("isActive") is not False:
        return (
            False,
            f"Expected Google Pay isActive to be False, but got {google_pay.get('isActive')}.",
        )

    return True, "Both PayPal and Google Pay are turned off."
