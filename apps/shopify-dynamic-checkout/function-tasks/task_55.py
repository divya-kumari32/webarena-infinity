import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that both Amazon Pay and Venmo are activated."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    payment_methods = state.get("paymentMethods", [])

    amazon_pay = next((pm for pm in payment_methods if pm["name"] == "Amazon Pay"), None)
    if not amazon_pay:
        return False, "Payment method 'Amazon Pay' not found."

    venmo = next((pm for pm in payment_methods if pm["name"] == "Venmo"), None)
    if not venmo:
        return False, "Payment method 'Venmo' not found."

    if amazon_pay.get("isActive") is not True:
        return False, f"Expected Amazon Pay isActive to be true, got '{amazon_pay.get('isActive')}'."

    if venmo.get("isActive") is not True:
        return False, f"Expected Venmo isActive to be true, got '{venmo.get('isActive')}'."

    return True, "Both Amazon Pay and Venmo are activated."
