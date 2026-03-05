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

    # Check Dawn button colors
    dawn_settings = dawn.get("settings", {})
    dawn_colors = dawn_settings.get("colors", {})

    accent_bg = dawn_colors.get("accentButtonBg", "")
    if accent_bg.upper() != "#FFFFFF":
        return False, (
            f"Expected Dawn accentButtonBg to be '#FFFFFF', but got '{accent_bg}'."
        )

    accent_text = dawn_colors.get("accentButtonText", "")
    if accent_text.upper() != "#1A1A1A":
        return False, (
            f"Expected Dawn accentButtonText to be '#1A1A1A', but got '{accent_text}'."
        )

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

    # Find 'Linen Blend Blazer' product
    linen_blazer = next((p for p in products if p.get("title") == "Linen Blend Blazer"), None)
    if linen_blazer is None:
        return False, "Product 'Linen Blend Blazer' not found in state."

    # Check featured section productId matches Linen Blend Blazer
    section_product_id = featured_section.get("productId")
    blazer_id = linen_blazer.get("id")
    if section_product_id != blazer_id:
        return False, (
            f"Expected featured product section productId to be '{blazer_id}' "
            f"(Linen Blend Blazer), but got '{section_product_id}'."
        )

    # Check section showAcceleratedCheckout is False
    if featured_section.get("showAcceleratedCheckout") is not False:
        return False, (
            f"Expected featured product section showAcceleratedCheckout to be False, "
            f"but got '{featured_section.get('showAcceleratedCheckout')}'."
        )

    return True, (
        "Dawn button colors set to white bg (#FFFFFF) and dark text (#1A1A1A), "
        "featured product changed to Linen Blend Blazer, and checkout disabled on section."
    )
