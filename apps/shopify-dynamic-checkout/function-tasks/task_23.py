import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that accelerated checkout is disabled on the featured product section of Dawn's Home page."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    dawn = next((t for t in themes if t["name"] == "Dawn"), None)
    if not dawn:
        return False, "Theme 'Dawn' not found."

    # Find Dawn's home page
    theme_pages = state.get("themePages", [])
    home_page = next(
        (p for p in theme_pages if p.get("type") == "home" and p["themeId"] == dawn["id"]),
        None,
    )
    if not home_page:
        return False, "Home page for Dawn theme not found."

    # Find featured_product section on that page
    theme_sections = state.get("themeSections", [])
    featured_section = next(
        (s for s in theme_sections if s.get("type") == "featured_product" and s["pageId"] == home_page["id"]),
        None,
    )
    if not featured_section:
        return False, "Featured product section on Dawn's Home page not found."

    if featured_section.get("showAcceleratedCheckout") is not False:
        return False, (
            f"Expected showAcceleratedCheckout to be false on featured product section, "
            f"got '{featured_section.get('showAcceleratedCheckout')}'."
        )

    return True, "Accelerated checkout is disabled on the featured product section of Dawn's Home page."
