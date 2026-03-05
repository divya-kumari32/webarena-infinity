import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    payment_methods = state.get("paymentMethods", [])
    google_pay = next((p for p in payment_methods if p.get("name") == "Google Pay"), None)
    if google_pay is None:
        return False, "Payment method 'Google Pay' not found in state."

    if google_pay.get("isActive") is not False:
        return False, f"Expected Google Pay isActive to be False, but got {google_pay.get('isActive')}."

    return True, "Google Pay is turned off."
