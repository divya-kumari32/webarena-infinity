import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Cheapest Stride Lab product → featured product, disable section checkout, Dawn button font Inter."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    products = state.get("products", [])
    sections = state.get("themeSections", [])
    themes = state.get("themes", [])

    # In seed data, Stride Lab products and their lowest variant prices:
    # Canvas Sneakers: $54.99, Titanium Watch: $349.99, Yoga Pants: $58.99,
    # Running Shorts: $44.99, Base Layer: $79.99
    # Cheapest individual variant = Running Shorts at $44.99

    # Find the product with lowest variant price among Stride Lab
    stride_lab = [p for p in products if p.get("vendor") == "Stride Lab"]
    if not stride_lab:
        return False, "No Stride Lab products found."

    min_price = float("inf")
    cheapest = None
    for p in stride_lab:
        for v in p.get("variants", []):
            price = float(v.get("price", 0))
            if price < min_price:
                min_price = price
                cheapest = p

    if cheapest is None:
        return False, "Could not determine cheapest Stride Lab product."

    # Check featured product section
    featured_sec = next(
        (s for s in sections
         if s.get("type") == "featured_product" and s.get("pageId") == "page_home"),
        None
    )
    if featured_sec is None:
        return False, "Featured product section not found on home page."

    if featured_sec.get("productId") != cheapest["id"]:
        actual = next((p for p in products if p.get("id") == featured_sec.get("productId")), {})
        return False, (f"Expected featured product '{cheapest['title']}' (${min_price}), "
                      f"but found '{actual.get('title', 'unknown')}'.")

    if featured_sec.get("showAcceleratedCheckout") is not False:
        return False, (f"Expected section checkout disabled, "
                      f"got {featured_sec.get('showAcceleratedCheckout')}.")

    # Check Dawn button font
    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found."
    button_font = dawn.get("settings", {}).get("typography", {}).get("buttonFont")
    if button_font != "Inter":
        return False, f"Expected Dawn button font 'Inter', got '{button_font}'."

    return True, (f"Featured product set to '{cheapest['title']}' (${min_price}). "
                  f"Section checkout disabled. Dawn button font: Inter.")
