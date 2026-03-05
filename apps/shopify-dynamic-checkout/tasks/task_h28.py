import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    templates = state.get("templates", [])
    payment_methods = state.get("paymentMethods", [])

    # Check Ride is published
    ride = next((t for t in themes if t.get("name") == "Ride"), None)
    if ride is None:
        return False, "Theme 'Ride' not found."
    if ride.get("role") != "main":
        return False, f"Expected Ride to be published (role='main'), but got role='{ride.get('role')}'."

    # Check Ride's button background matches Dawn's original accent color (#4F46E5)
    ride_colors = ride.get("settings", {}).get("colors", {})
    expected_color = "#4F46E5"
    if ride_colors.get("accentButtonBg", "").upper() != expected_color.upper():
        return False, (
            f"Expected Ride accentButtonBg to be '{expected_color}' (Dawn's accent color), "
            f"but got '{ride_colors.get('accentButtonBg')}'."
        )

    # Check Amazon Pay is active
    amazon = next((m for m in payment_methods if m.get("name") == "Amazon Pay"), None)
    if amazon is None:
        return False, "Payment method 'Amazon Pay' not found."
    if amazon.get("isActive") is not True:
        return False, f"Expected Amazon Pay to be active, but got isActive={amazon.get('isActive')}."

    # Check Ride's default template buy button text
    ride_default = next(
        (t for t in templates if t.get("themeId") == ride["id"] and t.get("isDefault") is True),
        None
    )
    if ride_default is None:
        return False, "Ride's default template not found."
    if ride_default.get("buyButtonText") != "Buy it now":
        return False, (
            f"Expected Ride default template buyButtonText='Buy it now', "
            f"but got '{ride_default.get('buyButtonText')}'."
        )

    return True, (
        "Ride published, button background set to Dawn's accent color (#4F46E5), "
        "Amazon Pay activated, buy button text set to 'Buy it now'."
    )
