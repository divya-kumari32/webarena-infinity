import requests
from collections import Counter


def verify(server_url: str) -> tuple[bool, str]:
    """Find product type with most active products → create template → assign → disable default."""
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

    # Determine the top product type from seed data
    # Seed active products by type: Apparel=5, Accessories=3, Activewear=3, Outerwear=2, Home=2, etc.
    top_type = "Apparel"

    # Check new template exists
    top_tmpl = next(
        (t for t in templates
         if t.get("themeId") == dawn["id"] and t.get("name") == "Product - Top Category"),
        None
    )
    if top_tmpl is None:
        return False, "Template 'Product - Top Category' not found on Dawn."

    if top_tmpl.get("showAcceleratedCheckout") is not True:
        return False, (f"Expected 'Product - Top Category' checkout enabled, "
                      f"got {top_tmpl.get('showAcceleratedCheckout')}.")

    if top_tmpl.get("buyButtonText") != "Shop now":
        return False, (f"Expected buy button text 'Shop now', "
                      f"got '{top_tmpl.get('buyButtonText')}'.")

    # Check all active Apparel products are on the new template
    apparel_active = [p for p in products
                      if p.get("productType") == top_type and p.get("status") == "active"]
    for p in apparel_active:
        if p.get("templateId") != top_tmpl["id"]:
            return False, (f"Expected active Apparel product '{p['title']}' on "
                          f"'Product - Top Category', but it's on '{p.get('templateId')}'.")

    # Check default template has checkout disabled
    default_tmpl = next(
        (t for t in templates
         if t.get("themeId") == dawn["id"] and t.get("isDefault") is True),
        None
    )
    if default_tmpl is None:
        return False, "Dawn default template not found."
    if default_tmpl.get("showAcceleratedCheckout") is not False:
        return False, (f"Expected default template checkout disabled, "
                      f"got {default_tmpl.get('showAcceleratedCheckout')}.")

    return True, (f"Template 'Product - Top Category' created (checkout enabled, 'Shop now'). "
                  f"{len(apparel_active)} Apparel products assigned. Default template checkout disabled.")
