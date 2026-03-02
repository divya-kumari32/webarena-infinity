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

    # Find the home page for Dawn
    pages = state.get("themePages", [])
    home_page = next(
        (p for p in pages if p.get("themeId") == dawn_id and p.get("type") == "home"),
        None,
    )
    if home_page is None:
        return False, f"Home page not found for Dawn theme (id={dawn_id})."
    home_page_id = home_page.get("id")

    # Find the featured_product section on the home page
    sections = state.get("themeSections", [])
    featured_section = next(
        (s for s in sections if s.get("pageId") == home_page_id and s.get("type") == "featured_product"),
        None,
    )
    if featured_section is None:
        return False, f"Featured product section not found on home page (id={home_page_id})."

    # Find the Titanium Watch product
    products = state.get("products", [])
    titanium_watch = next((p for p in products if "Titanium Watch" in p.get("title", "")), None)
    if titanium_watch is None:
        return False, "Product with title containing 'Titanium Watch' not found in state."
    watch_id = titanium_watch.get("id")

    if featured_section.get("productId") != watch_id:
        return (
            False,
            f"Expected home page featured product section productId to be '{watch_id}' (Titanium Watch), "
            f"but got '{featured_section.get('productId')}'.",
        )

    return True, "Home page featured product is set to Titanium Watch."
