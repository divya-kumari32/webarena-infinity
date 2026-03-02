import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    sections = state.get("themeSections", [])
    products = state.get("products", [])
    pages = state.get("themePages", [])

    # Find Dawn theme
    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found in state."
    dawn_id = dawn.get("id")

    # Find Dawn home page
    home_page = next(
        (p for p in pages if p.get("themeId") == dawn_id and p.get("type") == "home"),
        None
    )
    if home_page is None:
        return False, "Dawn home page not found in state."
    home_page_id = home_page.get("id")

    # Find featured_product section on home page
    featured_section = next(
        (s for s in sections if s.get("themeId") == dawn_id and s.get("pageId") == home_page_id and s.get("type") == "featured_product"),
        None
    )
    if featured_section is None:
        return False, "Featured product section not found on Dawn home page."

    # Find 'Organic Denim Jacket' product
    denim_jacket = next(
        (p for p in products if p.get("title") == "Organic Denim Jacket"),
        None
    )
    if denim_jacket is None:
        return False, "Product 'Organic Denim Jacket' not found in state."

    # Check featured section productId matches Organic Denim Jacket
    section_product_id = featured_section.get("productId")
    jacket_id = denim_jacket.get("id")
    if section_product_id != jacket_id:
        return False, (
            f"Expected featured product section productId to be '{jacket_id}' "
            f"(Organic Denim Jacket), but got '{section_product_id}'."
        )

    # Check section showAcceleratedCheckout is False
    if featured_section.get("showAcceleratedCheckout") is not False:
        return False, (
            f"Expected featured product section showAcceleratedCheckout to be False, "
            f"but got '{featured_section.get('showAcceleratedCheckout')}'."
        )

    return True, (
        "Home page featured product changed to Organic Denim Jacket "
        "and checkout disabled on the section."
    )
