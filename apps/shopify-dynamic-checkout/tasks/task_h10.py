import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    templates = state.get("templates", [])
    payment_methods = state.get("paymentMethods", [])

    # Check Ride is published (role == 'main')
    ride = next((t for t in themes if t.get("name") == "Ride"), None)
    if ride is None:
        return False, "Theme 'Ride' not found in state."
    if ride.get("role") != "main":
        return False, (
            f"Expected Ride theme role to be 'main', but got '{ride.get('role')}'."
        )
    ride_id = ride.get("id")

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

    # Check Ride default template has checkout enabled
    ride_default = next(
        (t for t in templates if t.get("themeId") == ride_id and t.get("isDefault") is True),
        None
    )
    if ride_default is None:
        return False, f"No default template found for Ride theme (themeId='{ride_id}')."
    if ride_default.get("showAcceleratedCheckout") is not True:
        return False, (
            f"Expected Ride default template to have showAcceleratedCheckout=True, "
            f"but got '{ride_default.get('showAcceleratedCheckout')}'."
        )

    return True, (
        "Ride is published, Amazon Pay and Venmo are activated, "
        "and Ride's default template has checkout enabled."
    )
