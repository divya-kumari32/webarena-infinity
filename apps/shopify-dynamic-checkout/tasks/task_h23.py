import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    payment_methods = state.get("paymentMethods", [])
    shop_promise = state.get("shopPromise", {})

    # Count active accelerated payment methods
    active_accelerated = [
        m for m in payment_methods
        if m.get("type") == "accelerated" and m.get("isActive") is True
    ]
    count = len(active_accelerated)

    # In seed state there are 4 active accelerated methods
    expected_min = 4
    expected_max = 8

    # Check Shop Promise is active
    if shop_promise.get("isActive") is not True:
        return False, (
            f"Expected Shop Promise to be active, "
            f"but got isActive={shop_promise.get('isActive')}."
        )

    delivery = shop_promise.get("estimatedDeliveryDays", {})
    actual_min = delivery.get("min")
    actual_max = delivery.get("max")

    if actual_min != expected_min:
        return False, (
            f"Expected minimum delivery days to be {expected_min} "
            f"(number of active accelerated methods), but got {actual_min}."
        )

    if actual_max != expected_max:
        return False, (
            f"Expected maximum delivery days to be {expected_max} "
            f"(double the active accelerated methods count), but got {actual_max}."
        )

    threshold = shop_promise.get("freeShippingThreshold")
    if threshold != 100 and threshold != 100.0:
        return False, (
            f"Expected free shipping threshold to be $100, but got ${threshold}."
        )

    return True, (
        f"Shop Promise enabled with {expected_min}-{expected_max} day delivery "
        f"(based on {count} active accelerated methods) and $100 threshold."
    )
