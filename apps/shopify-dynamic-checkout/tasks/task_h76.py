import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Activate archived product, move it + same-vendor Outerwear to No checkout, enable checkout."""
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
        return False, "Template 'Product - No checkout buttons' not found."

    # Seed: only archived product = Heavyweight Hoodie (Urban Thread Co., Apparel)
    hoodie = next((p for p in products
                   if "Heavyweight Hoodie" in p.get("title", "")), None)
    if hoodie is None:
        return False, "Heavyweight Hoodie not found."
    if hoodie.get("status") != "active":
        return False, (f"Expected Heavyweight Hoodie active, "
                      f"got status='{hoodie.get('status')}'.")

    # Same vendor (Urban Thread Co.) Outerwear products:
    # Recycled Polyester Windbreaker, Organic Denim Jacket
    vendor = "Urban Thread Co."
    target_products = [hoodie]
    for p in products:
        if (p.get("vendor") == vendor
                and p.get("productType") == "Outerwear"
                and p["id"] != hoodie["id"]):
            target_products.append(p)

    for p in target_products:
        if p.get("templateId") != no_checkout["id"]:
            return False, (f"Expected '{p['title']}' on 'No checkout buttons', "
                          f"but it's on template '{p.get('templateId')}'.")

    if no_checkout.get("showAcceleratedCheckout") is not True:
        return False, (f"Expected 'No checkout buttons' checkout enabled, "
                      f"got {no_checkout.get('showAcceleratedCheckout')}.")

    return True, (f"Heavyweight Hoodie activated. {len(target_products)} products "
                  f"moved to 'No checkout buttons' with checkout enabled.")
