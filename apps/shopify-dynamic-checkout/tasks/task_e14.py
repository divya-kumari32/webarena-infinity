import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found in state."
    dawn_id = dawn.get("id")

    pages = state.get("themePages", [])
    home_page = next(
        (p for p in pages if p.get("themeId") == dawn_id and p.get("type") == "home"), None
    )
    if home_page is None:
        return False, f"Home page not found for Dawn theme (id={dawn_id})."
    home_page_id = home_page.get("id")

    sections = state.get("themeSections", [])
    featured_product = next(
        (s for s in sections if s.get("pageId") == home_page_id and s.get("type") == "featured_product"),
        None,
    )
    if featured_product is None:
        return False, f"Featured product section not found on Dawn's home page (pageId={home_page_id})."

    if featured_product.get("showAcceleratedCheckout") is not False:
        return (
            False,
            f"Expected showAcceleratedCheckout to be False on the home page's featured product section, "
            f"but got {featured_product.get('showAcceleratedCheckout')}.",
        )

    return True, "Accelerated checkout is turned off on the home page's featured product section."
