import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    payment_methods = state.get("paymentMethods", [])
    shop_promise = state.get("shopPromise", {})

    accelerated = [m for m in payment_methods if m.get("type") == "accelerated"]

    # Check restricted methods are inactive
    for m in accelerated:
        has_restriction = (
            m.get("browserRestrictions") is not None or
            (m.get("regionRestrictions") is not None and len(m.get("regionRestrictions", [])) > 0)
        )
        if has_restriction:
            if m.get("isActive") is not False:
                return False, (
                    f"Expected '{m['name']}' (has restrictions) to be deactivated, "
                    f"but got isActive={m.get('isActive')}."
                )

    # Check unrestricted methods are active
    for m in accelerated:
        has_restriction = (
            m.get("browserRestrictions") is not None or
            (m.get("regionRestrictions") is not None and len(m.get("regionRestrictions", [])) > 0)
        )
        if not has_restriction:
            if m.get("isActive") is not True:
                return False, (
                    f"Expected '{m['name']}' (no restrictions) to be activated, "
                    f"but got isActive={m.get('isActive')}."
                )

    # Check free shipping threshold
    threshold = shop_promise.get("freeShippingThreshold")
    if threshold != 50 and threshold != 50.0:
        return False, (
            f"Expected free shipping threshold to be $50, but got ${threshold}."
        )

    # Check Shop Promise is NOT enabled
    if shop_promise.get("isActive") is not False:
        return False, (
            f"Expected Shop Promise to remain disabled (isActive=False), "
            f"but got isActive={shop_promise.get('isActive')}."
        )

    return True, (
        "Restricted payment methods (Apple Pay, Venmo) deactivated, "
        "unrestricted methods (Shop Pay, Google Pay, PayPal, Amazon Pay) activated, "
        "free shipping threshold set to $50, Shop Promise remains disabled."
    )
