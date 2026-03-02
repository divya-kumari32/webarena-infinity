import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Shop Pay is deactivated."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    payment_methods = state.get("paymentMethods", [])
    shop_pay = next((p for p in payment_methods if p["name"] == "Shop Pay"), None)
    if not shop_pay:
        return False, "Payment method 'Shop Pay' not found."

    if shop_pay.get("isActive") is not False:
        return False, f"Expected Shop Pay isActive to be false, got '{shop_pay.get('isActive')}'."

    return True, "Shop Pay is deactivated."
