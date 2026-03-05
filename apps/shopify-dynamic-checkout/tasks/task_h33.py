import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    shop_promise = state.get("shopPromise", {})
    payment_methods = state.get("paymentMethods", [])
    themes = state.get("themes", [])

    # Check Shop Promise
    if shop_promise.get("isActive") is not True:
        return False, f"Expected Shop Promise active, but got isActive={shop_promise.get('isActive')}."

    delivery = shop_promise.get("estimatedDeliveryDays", {})
    if delivery.get("min") != 2:
        return False, f"Expected minimum delivery days 2, but got {delivery.get('min')}."
    if delivery.get("max") != 7:
        return False, f"Expected maximum delivery days 7, but got {delivery.get('max')}."

    # Check PayPal deactivated
    paypal = next((m for m in payment_methods if m.get("name") == "PayPal"), None)
    if paypal is None:
        return False, "Payment method 'PayPal' not found."
    if paypal.get("isActive") is not False:
        return False, f"Expected PayPal deactivated, but got isActive={paypal.get('isActive')}."

    # Check Amazon Pay activated
    amazon = next((m for m in payment_methods if m.get("name") == "Amazon Pay"), None)
    if amazon is None:
        return False, "Payment method 'Amazon Pay' not found."
    if amazon.get("isActive") is not True:
        return False, f"Expected Amazon Pay activated, but got isActive={amazon.get('isActive')}."

    # Check Dawn button colors
    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found."

    colors = dawn.get("settings", {}).get("colors", {})
    if colors.get("accentButtonBg", "").upper() != "#DC2626":
        return False, (
            f"Expected Dawn accentButtonBg '#DC2626', "
            f"but got '{colors.get('accentButtonBg')}'."
        )
    if colors.get("accentButtonText", "").upper() != "#FFFFFF":
        return False, (
            f"Expected Dawn accentButtonText '#FFFFFF', "
            f"but got '{colors.get('accentButtonText')}'."
        )

    return True, (
        "Shop Promise enabled (2-7 days), PayPal deactivated, Amazon Pay activated, "
        "Dawn button colors set to red (#DC2626) with white text."
    )
