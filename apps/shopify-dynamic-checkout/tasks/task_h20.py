import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    payment_methods = state.get("paymentMethods", [])
    apps = state.get("installedApps", [])
    cart_attrs = state.get("cartAttributes", [])

    # Check Amazon Pay is active
    amazon_pay = next((m for m in payment_methods if m.get("name") == "Amazon Pay"), None)
    if amazon_pay is None:
        return False, "Payment method 'Amazon Pay' not found in state."
    if amazon_pay.get("isActive") is not True:
        return False, (
            f"Expected Amazon Pay to be active (isActive=True), "
            f"but got isActive={amazon_pay.get('isActive')}."
        )

    # Check Venmo is active
    venmo = next((m for m in payment_methods if m.get("name") == "Venmo"), None)
    if venmo is None:
        return False, "Payment method 'Venmo' not found in state."
    if venmo.get("isActive") is not True:
        return False, (
            f"Expected Venmo to be active (isActive=True), "
            f"but got isActive={venmo.get('isActive')}."
        )

    # Check conflicting apps are deactivated
    conflicting_apps = [
        "Currency Converter Plus",
        "Oberlo Dropshipping",
        "ReConvert Upsell & Cross Sell",
    ]
    for app_name in conflicting_apps:
        app = next((a for a in apps if a.get("name") == app_name), None)
        if app is None:
            return False, f"App '{app_name}' not found in state."
        if app.get("isActive") is not False:
            return False, (
                f"Expected app '{app_name}' to be deactivated (isActive=False), "
                f"but got isActive={app.get('isActive')}."
            )

    # Check Terms and conditions cart attribute is active
    terms_attr = next(
        (a for a in cart_attrs if a.get("name") == "Terms and conditions"),
        None
    )
    if terms_attr is None:
        return False, "Cart attribute 'Terms and conditions' not found in state."
    if terms_attr.get("isActive") is not True:
        return False, (
            f"Expected cart attribute 'Terms and conditions' to be active (isActive=True), "
            f"but got isActive={terms_attr.get('isActive')}."
        )

    return True, (
        "Amazon Pay and Venmo activated, all conflicting apps deactivated, "
        "and Terms and conditions enabled."
    )
