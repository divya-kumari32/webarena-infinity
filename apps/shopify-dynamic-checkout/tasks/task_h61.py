import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Count active accelerated methods → Shop Promise config → deactivate PayPal."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    shop_promise = state.get("shopPromise", {})
    payment_methods = state.get("paymentMethods", [])

    # In seed state, 4 accelerated methods are active (Shop Pay, Apple Pay, Google Pay, PayPal)
    expected_count = 4

    # Check Shop Promise is enabled
    if shop_promise.get("isActive") is not True:
        return False, f"Expected Shop Promise enabled, got isActive={shop_promise.get('isActive')}."

    delivery = shop_promise.get("estimatedDeliveryDays", {})
    if delivery.get("min") != expected_count:
        return False, f"Expected min delivery days {expected_count}, got {delivery.get('min')}."
    if delivery.get("max") != expected_count + 3:
        return False, f"Expected max delivery days {expected_count + 3}, got {delivery.get('max')}."

    threshold = shop_promise.get("freeShippingThreshold")
    if threshold != 55 and threshold != 55.0:
        return False, f"Expected free shipping threshold $55, got ${threshold}."

    # Check PayPal is deactivated
    paypal = next((m for m in payment_methods if m.get("name") == "PayPal"), None)
    if paypal is None:
        return False, "PayPal payment method not found."
    if paypal.get("isActive") is not False:
        return False, f"Expected PayPal deactivated, got isActive={paypal.get('isActive')}."

    return True, (f"Shop Promise enabled (min={expected_count}, max={expected_count + 3}, "
                  f"threshold=$55). PayPal deactivated.")
