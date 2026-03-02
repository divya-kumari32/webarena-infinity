import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that all 4 active accelerated payment methods (Shop Pay, Apple Pay, Google Pay, PayPal) are deactivated."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    payment_methods = state.get("paymentMethods", [])
    target_names = ["Shop Pay", "Apple Pay", "Google Pay", "PayPal"]

    for name in target_names:
        method = next((m for m in payment_methods if m["name"] == name), None)
        if not method:
            return False, f"Payment method '{name}' not found."
        if method.get("isActive") is not False:
            return False, f"Expected '{name}' isActive to be false, got '{method.get('isActive')}'."

    return True, "All 4 accelerated payment methods (Shop Pay, Apple Pay, Google Pay, PayPal) are deactivated."
