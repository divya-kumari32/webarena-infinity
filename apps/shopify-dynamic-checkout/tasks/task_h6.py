import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    templates = state.get("templates", [])
    payment_methods = state.get("paymentMethods", [])

    # Find Dawn theme
    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found in state."
    dawn_id = dawn.get("id")

    # Check all Dawn templates have showAcceleratedCheckout == False
    dawn_templates = [t for t in templates if t.get("themeId") == dawn_id]
    if not dawn_templates:
        return False, f"No templates found for Dawn theme (themeId='{dawn_id}')."

    for tmpl in dawn_templates:
        if tmpl.get("showAcceleratedCheckout") is not False:
            return False, (
                f"Expected Dawn template '{tmpl.get('name')}' (id='{tmpl.get('id')}') "
                f"to have showAcceleratedCheckout=False, but got "
                f"'{tmpl.get('showAcceleratedCheckout')}'."
            )

    # Check all accelerated payment methods are deactivated
    accel_methods = ["Shop Pay", "Apple Pay", "Google Pay", "PayPal"]
    for method_name in accel_methods:
        method = next((m for m in payment_methods if m.get("name") == method_name), None)
        if method is None:
            return False, f"Payment method '{method_name}' not found in state."
        if method.get("isActive") is not False:
            return False, (
                f"Expected payment method '{method_name}' to be deactivated (isActive=False), "
                f"but got isActive={method.get('isActive')}."
            )

    return True, (
        "All Dawn templates have checkout disabled, and all accelerated payment methods "
        "(Shop Pay, Apple Pay, Google Pay, PayPal) are deactivated."
    )
