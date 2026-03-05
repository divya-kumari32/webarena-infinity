import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Amazon Pay is activated."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    payment_methods = state.get("paymentMethods", [])
    amazon_pay = next((p for p in payment_methods if p["name"] == "Amazon Pay"), None)
    if not amazon_pay:
        return False, "Payment method 'Amazon Pay' not found."

    if amazon_pay.get("isActive") is not True:
        return False, f"Expected Amazon Pay isActive to be true, got '{amazon_pay.get('isActive')}'."

    return True, "Amazon Pay is activated."
