import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    templates = state.get("templates", [])
    products = state.get("products", [])
    payment_methods = state.get("paymentMethods", [])

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

    # Find Dawn theme
    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found in state."
    dawn_id = dawn.get("id")

    # Find 'Product - Quick Buy' template on Dawn
    quick_buy_tmpl = next(
        (t for t in templates if t.get("themeId") == dawn_id and t.get("name") == "Product - Quick Buy"),
        None
    )
    if quick_buy_tmpl is None:
        return False, f"Template 'Product - Quick Buy' not found on Dawn (themeId='{dawn_id}')."

    quick_buy_id = quick_buy_tmpl.get("id")

    if quick_buy_tmpl.get("showAcceleratedCheckout") is not True:
        return False, (
            f"Expected 'Product - Quick Buy' template to have showAcceleratedCheckout=True, "
            f"but got '{quick_buy_tmpl.get('showAcceleratedCheckout')}'."
        )

    # Check Canvas Sneakers assigned to Quick Buy template
    canvas_sneakers = next((p for p in products if p.get("title") == "Canvas Sneakers"), None)
    if canvas_sneakers is None:
        return False, "Product 'Canvas Sneakers' not found in state."
    if canvas_sneakers.get("templateId") != quick_buy_id:
        return False, (
            f"Expected 'Canvas Sneakers' to have templateId='{quick_buy_id}' "
            f"(Product - Quick Buy), but got '{canvas_sneakers.get('templateId')}'."
        )

    return True, (
        "Amazon Pay and Venmo activated, 'Product - Quick Buy' template created on Dawn "
        "with checkout enabled, and Canvas Sneakers assigned to it."
    )
