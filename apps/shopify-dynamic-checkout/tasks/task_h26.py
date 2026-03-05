import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    products = state.get("products", [])
    sections = state.get("themeSections", [])

    # The seed state's featured product was Classic Cotton T-Shirt (prod_1)
    cotton_tshirt = next((p for p in products if p.get("title") == "Classic Cotton T-Shirt"), None)
    if cotton_tshirt is None:
        return False, "Product 'Classic Cotton T-Shirt' not found."

    # Check it's been set to draft
    if cotton_tshirt.get("status") != "draft":
        return False, (
            f"Expected Classic Cotton T-Shirt (original featured product) to be in 'draft' status, "
            f"but got '{cotton_tshirt.get('status')}'."
        )

    # Find Bamboo Fiber Socks
    bamboo_socks = next(
        (p for p in products if "Bamboo Fiber Socks" in p.get("title", "")),
        None
    )
    if bamboo_socks is None:
        return False, "Product 'Bamboo Fiber Socks' not found."

    # Check featured product section
    featured_sec = next(
        (s for s in sections if s.get("type") == "featured_product" and s.get("pageId") == "page_home"),
        None
    )
    if featured_sec is None:
        return False, "Featured product section not found on home page."

    if featured_sec.get("productId") != bamboo_socks["id"]:
        return False, (
            f"Expected featured product to be Bamboo Fiber Socks (id='{bamboo_socks['id']}'), "
            f"but got productId='{featured_sec.get('productId')}'."
        )

    # Check accelerated checkout is disabled on section
    if featured_sec.get("showAcceleratedCheckout") is not False:
        return False, (
            f"Expected accelerated checkout disabled on featured product section, "
            f"but got showAcceleratedCheckout={featured_sec.get('showAcceleratedCheckout')}."
        )

    return True, (
        "Classic Cotton T-Shirt set to draft, Bamboo Fiber Socks set as featured product, "
        "and accelerated checkout disabled on section."
    )
