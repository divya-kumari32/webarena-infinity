import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    payment_methods = state.get("paymentMethods", [])
    apple_pay = next((p for p in payment_methods if p.get("name") == "Apple Pay"), None)
    if apple_pay is None:
        return False, "Payment method 'Apple Pay' not found in state."

    if apple_pay.get("isActive") is not False:
        return False, f"Expected Apple Pay isActive to be False, but got {apple_pay.get('isActive')}."

    return True, "Apple Pay is deactivated."
