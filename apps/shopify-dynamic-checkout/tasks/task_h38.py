import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    templates = state.get("templates", [])
    sections = state.get("themeSections", [])

    # Find Dawn
    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found."

    # Find 'No checkout buttons' template
    no_checkout = next(
        (t for t in templates
         if t.get("themeId") == dawn["id"] and t.get("name") == "Product - No checkout buttons"),
        None
    )
    if no_checkout is None:
        return False, "Template 'Product - No checkout buttons' not found on Dawn."

    # Check checkout enabled on 'No checkout buttons' template
    if no_checkout.get("showAcceleratedCheckout") is not True:
        return False, (
            f"Expected 'Product - No checkout buttons' template showAcceleratedCheckout=True, "
            f"but got {no_checkout.get('showAcceleratedCheckout')}."
        )

    # Check buy button text
    if no_checkout.get("buyButtonText") != "Quick add":
        return False, (
            f"Expected buyButtonText='Quick add', "
            f"but got '{no_checkout.get('buyButtonText')}'."
        )

    # Check featured product section checkout disabled
    featured_sec = next(
        (s for s in sections if s.get("type") == "featured_product" and s.get("pageId") == "page_home"),
        None
    )
    if featured_sec is None:
        return False, "Featured product section not found on home page."

    if featured_sec.get("showAcceleratedCheckout") is not False:
        return False, (
            f"Expected featured product section showAcceleratedCheckout=False, "
            f"but got {featured_sec.get('showAcceleratedCheckout')}."
        )

    return True, (
        "'No checkout buttons' template: checkout enabled, buy button text 'Quick add'. "
        "Home page featured product section: checkout disabled."
    )
