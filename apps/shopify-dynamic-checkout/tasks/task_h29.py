import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    templates = state.get("templates", [])
    products = state.get("products", [])

    # Find Dawn
    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found."

    # Find 'Product - Active Gear' template on Dawn
    active_gear = next(
        (t for t in templates
         if t.get("themeId") == dawn["id"] and t.get("name") == "Product - Active Gear"),
        None
    )
    if active_gear is None:
        return False, "Template 'Product - Active Gear' not found on Dawn."

    # Check template settings
    if active_gear.get("showAcceleratedCheckout") is not True:
        return False, (
            f"Expected 'Product - Active Gear' to have showAcceleratedCheckout=True, "
            f"but got {active_gear.get('showAcceleratedCheckout')}."
        )

    if active_gear.get("buyButtonText") != "Get moving":
        return False, (
            f"Expected buyButtonText='Get moving', "
            f"but got '{active_gear.get('buyButtonText')}'."
        )

    # Check all Activewear products are assigned to this template
    activewear_products = [p for p in products if p.get("productType") == "Activewear"]
    if not activewear_products:
        return False, "No Activewear products found."

    for p in activewear_products:
        if p.get("templateId") != active_gear["id"]:
            return False, (
                f"Activewear product '{p['title']}' has templateId='{p.get('templateId')}', "
                f"expected '{active_gear['id']}' (Product - Active Gear)."
            )

    names = [p["title"] for p in activewear_products]
    return True, (
        f"'Product - Active Gear' template created on Dawn with checkout enabled "
        f"and buy button 'Get moving'. Activewear products assigned: {', '.join(names)}."
    )
