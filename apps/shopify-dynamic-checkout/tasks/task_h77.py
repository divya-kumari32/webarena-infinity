import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Featured product=Silk Scarf, section checkout enabled, default template text+qty changes."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    templates = state.get("templates", [])
    products = state.get("products", [])
    sections = state.get("themeSections", [])

    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found."

    # Check featured product section
    featured_sec = next(
        (s for s in sections
         if s.get("type") == "featured_product" and s.get("pageId") == "page_home"),
        None
    )
    if featured_sec is None:
        return False, "Featured product section not found on home page."

    scarf = next((p for p in products if p.get("title") == "Silk Blend Scarf"), None)
    if scarf is None:
        return False, "Silk Blend Scarf not found."

    if featured_sec.get("productId") != scarf["id"]:
        actual = next((p for p in products if p.get("id") == featured_sec.get("productId")), {})
        return False, (f"Expected featured product 'Silk Blend Scarf', "
                      f"but found '{actual.get('title', 'unknown')}'.")

    if featured_sec.get("showAcceleratedCheckout") is not True:
        return False, (f"Expected featured section checkout enabled, "
                      f"got {featured_sec.get('showAcceleratedCheckout')}.")

    # Check default template
    default_tmpl = next(
        (t for t in templates
         if t.get("themeId") == dawn["id"] and t.get("isDefault") is True),
        None
    )
    if default_tmpl is None:
        return False, "Dawn default template not found."

    if default_tmpl.get("buyButtonText") != "Add to collection":
        return False, (f"Expected default template buy text 'Add to collection', "
                      f"got '{default_tmpl.get('buyButtonText')}'.")
    if default_tmpl.get("showQuantitySelector") is not False:
        return False, (f"Expected default template quantity selector disabled, "
                      f"got {default_tmpl.get('showQuantitySelector')}.")

    return True, ("Featured product: Silk Blend Scarf (checkout enabled). "
                  "Default template: 'Add to collection', quantity selector disabled.")
