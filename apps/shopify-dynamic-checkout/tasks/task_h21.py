import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    sections = state.get("themeSections", [])
    products = state.get("products", [])

    # Find featured product section on home page
    featured_sec = next(
        (s for s in sections if s.get("type") == "featured_product" and s.get("pageId") == "page_home"),
        None
    )
    if featured_sec is None:
        return False, "Featured product section not found on home page."

    # Find the product with the highest individual variant price
    max_price = 0
    max_product_id = None
    max_product_title = None
    for p in products:
        for v in p.get("variants", []):
            price = float(v.get("price", 0))
            if price > max_price:
                max_price = price
                max_product_id = p["id"]
                max_product_title = p["title"]

    if max_product_id is None:
        return False, "No products with variants found."

    # Check featured product matches
    if featured_sec.get("productId") != max_product_id:
        actual_product = next(
            (p for p in products if p.get("id") == featured_sec.get("productId")), {}
        )
        return False, (
            f"Expected featured product to be '{max_product_title}' (highest variant price ${max_price}), "
            f"but found '{actual_product.get('title', 'unknown')}' instead."
        )

    # Check accelerated checkout is disabled
    if featured_sec.get("showAcceleratedCheckout") is not False:
        return False, (
            f"Expected accelerated checkout to be disabled on featured product section, "
            f"but got showAcceleratedCheckout={featured_sec.get('showAcceleratedCheckout')}."
        )

    return True, (
        f"Featured product set to '{max_product_title}' (highest variant price ${max_price}) "
        f"and accelerated checkout disabled on section."
    )
