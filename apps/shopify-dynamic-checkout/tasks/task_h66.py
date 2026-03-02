import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Archive T-Shirt + Socks, move remaining active UTC to No checkout, enable checkout + text."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    templates = state.get("templates", [])
    products = state.get("products", [])

    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found."

    no_checkout = next(
        (t for t in templates
         if t.get("themeId") == dawn["id"] and t.get("name") == "Product - No checkout buttons"),
        None
    )
    if no_checkout is None:
        return False, "Template 'Product - No checkout buttons' not found on Dawn."

    # Check T-Shirt and Socks are archived
    tshirt = next((p for p in products if p.get("title") == "Classic Cotton T-Shirt"), None)
    socks = next((p for p in products
                  if "Bamboo Fiber Socks" in p.get("title", "")), None)
    if tshirt is None:
        return False, "Classic Cotton T-Shirt not found."
    if socks is None:
        return False, "Bamboo Fiber Socks not found."

    if tshirt.get("status") != "archived":
        return False, f"Expected T-Shirt archived, got status='{tshirt.get('status')}'."
    if socks.get("status") != "archived":
        return False, f"Expected Socks archived, got status='{socks.get('status')}'."

    # Remaining active UTC products should be on No checkout template
    # UTC products (excluding archived T-Shirt, archived Socks, and already-archived Hoodie):
    # Merino Wool Sweater, Slim Fit Chinos, Digital Gift Card, Windbreaker, Blazer, Denim Jacket
    utc_remaining_active = [
        p for p in products
        if p.get("vendor") == "Urban Thread Co."
        and p.get("status") == "active"
    ]
    for p in utc_remaining_active:
        if p.get("templateId") != no_checkout["id"]:
            return False, (f"Expected active UTC product '{p['title']}' on 'No checkout buttons', "
                          f"but it's on template '{p.get('templateId')}'.")

    # Check template settings
    if no_checkout.get("showAcceleratedCheckout") is not True:
        return False, (f"Expected 'No checkout buttons' checkout enabled, "
                      f"got {no_checkout.get('showAcceleratedCheckout')}.")
    if no_checkout.get("buyButtonText") != "Quick buy":
        return False, (f"Expected buy button text 'Quick buy', "
                      f"got '{no_checkout.get('buyButtonText')}'.")

    return True, (f"T-Shirt and Socks archived. {len(utc_remaining_active)} remaining active "
                  f"UTC products on 'No checkout buttons' (checkout enabled, 'Quick buy').")
