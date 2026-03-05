import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Deactivate conflicting apps/attrs, activate Amazon Pay, Shop Promise 1-3/$40, Dawn green button."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("installedApps", [])
    cart_attrs = state.get("cartAttributes", [])
    payment_methods = state.get("paymentMethods", [])
    shop_promise = state.get("shopPromise", {})
    themes = state.get("themes", [])

    # Check conflicting apps are deactivated
    for app in apps:
        if app.get("conflictsWithCheckout") is True:
            if app.get("isActive") is not False:
                return False, (f"Expected conflicting app '{app['name']}' deactivated, "
                              f"got isActive={app.get('isActive')}.")

    # Check conflicting cart attributes are disabled
    for attr in cart_attrs:
        if attr.get("conflictsWithCheckout") is True:
            if attr.get("isActive") is not False:
                return False, (f"Expected conflicting cart attr '{attr['name']}' disabled, "
                              f"got isActive={attr.get('isActive')}.")

    # Check Amazon Pay is active
    amazon = next((m for m in payment_methods if m.get("name") == "Amazon Pay"), None)
    if amazon and amazon.get("isActive") is not True:
        return False, f"Expected Amazon Pay active, got isActive={amazon.get('isActive')}."

    # Check Shop Promise
    if shop_promise.get("isActive") is not True:
        return False, f"Expected Shop Promise enabled, got isActive={shop_promise.get('isActive')}."
    delivery = shop_promise.get("estimatedDeliveryDays", {})
    if delivery.get("min") != 1:
        return False, f"Expected min delivery days 1, got {delivery.get('min')}."
    if delivery.get("max") != 3:
        return False, f"Expected max delivery days 3, got {delivery.get('max')}."
    threshold = shop_promise.get("freeShippingThreshold")
    if threshold != 40 and threshold != 40.0:
        return False, f"Expected free shipping threshold $40, got ${threshold}."

    # Check Dawn colors
    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found."
    dawn_colors = dawn.get("settings", {}).get("colors", {})
    if dawn_colors.get("accentButtonBg", "").upper() != "#16A34A":
        return False, f"Expected Dawn button bg '#16A34A', got '{dawn_colors.get('accentButtonBg')}'."
    if dawn_colors.get("accentButtonText", "").upper() != "#FFFFFF":
        return False, f"Expected Dawn button text '#FFFFFF', got '{dawn_colors.get('accentButtonText')}'."

    return True, ("Conflicting apps and cart attrs disabled. Amazon Pay active. "
                  "Shop Promise enabled (1-3 days, $40). Dawn button: #16A34A/#FFFFFF.")
