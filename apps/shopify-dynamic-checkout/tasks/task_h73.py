import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Deactivate setup-required methods, create template, move Stride Lab, Dawn font."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    templates = state.get("templates", [])
    products = state.get("products", [])
    payment_methods = state.get("paymentMethods", [])

    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found."

    # Check accelerated methods requiring setup are deactivated
    for pm in payment_methods:
        if pm.get("type") == "accelerated" and pm.get("requiresSetup") is True:
            if pm.get("isActive") is not False:
                return False, (f"Expected '{pm['name']}' (requires setup) deactivated, "
                              f"got isActive={pm.get('isActive')}.")

    # Check new template exists
    streamlined = next(
        (t for t in templates
         if t.get("themeId") == dawn["id"] and t.get("name") == "Product - Streamlined"),
        None
    )
    if streamlined is None:
        return False, "Template 'Product - Streamlined' not found on Dawn."

    if streamlined.get("showAcceleratedCheckout") is not True:
        return False, (f"Expected 'Product - Streamlined' checkout enabled, "
                      f"got {streamlined.get('showAcceleratedCheckout')}.")
    if streamlined.get("buyButtonText") != "Quick buy":
        return False, (f"Expected buy button text 'Quick buy', "
                      f"got '{streamlined.get('buyButtonText')}'.")

    # Check Stride Lab products are on the new template
    stride_lab = [p for p in products if p.get("vendor") == "Stride Lab"]
    for p in stride_lab:
        if p.get("templateId") != streamlined["id"]:
            return False, (f"Expected Stride Lab product '{p['title']}' on 'Product - Streamlined', "
                          f"but it's on template '{p.get('templateId')}'.")

    # Check Dawn button font
    typo = dawn.get("settings", {}).get("typography", {})
    if typo.get("buttonFont") != "Raleway":
        return False, f"Expected Dawn button font 'Raleway', got '{typo.get('buttonFont')}'."

    return True, (f"Setup-required methods deactivated. 'Product - Streamlined' created "
                  f"(checkout enabled, 'Quick buy'). {len(stride_lab)} Stride Lab products assigned. "
                  f"Dawn button font: Raleway.")
