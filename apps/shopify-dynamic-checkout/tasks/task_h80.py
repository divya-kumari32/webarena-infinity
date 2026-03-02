import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Publish Taste, deactivate all accel except Shop Pay, create Taste template, assign Beanie."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    templates = state.get("templates", [])
    products = state.get("products", [])
    payment_methods = state.get("paymentMethods", [])

    # Check Taste is published
    taste = next((t for t in themes if t.get("name") == "Taste"), None)
    if taste is None:
        return False, "Theme 'Taste' not found."
    if taste.get("role") != "main":
        return False, f"Expected Taste published (role='main'), got '{taste.get('role')}'."

    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn and dawn.get("role") == "main":
        return False, "Dawn should no longer be published."

    # Check accelerated payment methods: only Shop Pay active
    for pm in payment_methods:
        if pm.get("type") == "accelerated":
            if pm.get("name") == "Shop Pay":
                if pm.get("isActive") is not True:
                    return False, f"Expected Shop Pay active, got isActive={pm.get('isActive')}."
            else:
                if pm.get("isActive") is not False:
                    return False, (f"Expected '{pm['name']}' deactivated, "
                                  f"got isActive={pm.get('isActive')}.")

    # Check new template on Taste
    essential = next(
        (t for t in templates
         if t.get("themeId") == taste["id"] and t.get("name") == "Product - Essential"),
        None
    )
    if essential is None:
        return False, "Template 'Product - Essential' not found on Taste."

    if essential.get("showAcceleratedCheckout") is not True:
        return False, (f"Expected 'Product - Essential' checkout enabled, "
                      f"got {essential.get('showAcceleratedCheckout')}.")
    if essential.get("buyButtonText") != "Buy now":
        return False, (f"Expected buy button text 'Buy now', "
                      f"got '{essential.get('buyButtonText')}'.")

    # Check Cashmere Beanie is active and on the new template
    beanie = next((p for p in products if p.get("title") == "Cashmere Beanie"), None)
    if beanie is None:
        return False, "Cashmere Beanie not found."
    if beanie.get("status") != "active":
        return False, f"Expected Cashmere Beanie active, got status='{beanie.get('status')}'."
    if beanie.get("templateId") != essential["id"]:
        return False, (f"Expected Cashmere Beanie on 'Product - Essential', "
                      f"but it's on template '{beanie.get('templateId')}'.")

    return True, ("Taste published. All accel methods deactivated except Shop Pay. "
                  "'Product - Essential' created on Taste (checkout, 'Buy now'). "
                  "Cashmere Beanie activated and assigned.")
