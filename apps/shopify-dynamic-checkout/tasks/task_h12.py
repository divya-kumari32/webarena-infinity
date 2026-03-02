import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    payment_methods = state.get("paymentMethods", [])

    # Check Shop Pay is active
    shop_pay = next((m for m in payment_methods if m.get("name") == "Shop Pay"), None)
    if shop_pay is None:
        return False, "Payment method 'Shop Pay' not found in state."
    if shop_pay.get("isActive") is not True:
        return False, (
            f"Expected Shop Pay to be active (isActive=True), "
            f"but got isActive={shop_pay.get('isActive')}."
        )

    # Check other accelerated methods are deactivated
    deactivated_methods = ["Apple Pay", "Google Pay", "PayPal"]
    for method_name in deactivated_methods:
        method = next((m for m in payment_methods if m.get("name") == method_name), None)
        if method is None:
            return False, f"Payment method '{method_name}' not found in state."
        if method.get("isActive") is not False:
            return False, (
                f"Expected payment method '{method_name}' to be deactivated (isActive=False), "
                f"but got isActive={method.get('isActive')}."
            )

    # Check Shop Promise is enabled
    shop_promise = state.get("shopPromise", {})
    if shop_promise.get("isActive") is not True:
        return False, (
            f"Expected Shop Promise to be active (isActive=True), "
            f"but got isActive={shop_promise.get('isActive')}."
        )

    return True, (
        "Only Shop Pay remains active among accelerated methods, "
        "Apple Pay/Google Pay/PayPal deactivated, and Shop Promise enabled."
    )
