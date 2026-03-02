import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    payment_methods = state.get("paymentMethods", [])
    amazon_pay = next((p for p in payment_methods if p.get("name") == "Amazon Pay"), None)
    if amazon_pay is None:
        return False, "Payment method 'Amazon Pay' not found in state."

    if amazon_pay.get("isActive") is not True:
        return False, f"Expected Amazon Pay isActive to be True, but got {amazon_pay.get('isActive')}."

    return True, "Amazon Pay is enabled."
