import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("installedApps", [])
    cart_attrs = state.get("cartAttributes", [])

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

    # Check conflicting cart attributes are disabled
    conflicting_attrs = ["Gift wrapping", "Delivery date"]
    for attr_name in conflicting_attrs:
        attr = next((a for a in cart_attrs if a.get("name") == attr_name), None)
        if attr is None:
            return False, f"Cart attribute '{attr_name}' not found in state."
        if attr.get("isActive") is not False:
            return False, (
                f"Expected cart attribute '{attr_name}' to be disabled (isActive=False), "
                f"but got isActive={attr.get('isActive')}."
            )

    # Check Shop Promise is enabled
    shop_promise = state.get("shopPromise", {})
    if shop_promise.get("isActive") is not True:
        return False, (
            f"Expected Shop Promise to be active (isActive=True), "
            f"but got isActive={shop_promise.get('isActive')}."
        )

    return True, (
        "All conflicting apps deactivated, conflicting cart attributes disabled, "
        "and Shop Promise enabled."
    )
