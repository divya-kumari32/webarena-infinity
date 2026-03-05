import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    templates = state.get("templates", [])
    products = state.get("products", [])

    # Find Dawn theme
    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found in state."
    dawn_id = dawn.get("id")

    # Find 'Product - No checkout buttons' template on Dawn
    no_checkout_tmpl = next(
        (t for t in templates if t.get("themeId") == dawn_id and t.get("name") == "Product - No checkout buttons"),
        None
    )
    if no_checkout_tmpl is None:
        return False, (
            f"Template 'Product - No checkout buttons' not found on Dawn (themeId='{dawn_id}')."
        )
    no_checkout_id = no_checkout_tmpl.get("id")

    # Active Stride Lab products that should be assigned
    stride_lab_product_ids = ["prod_8", "prod_11", "prod_14", "prod_16", "prod_20"]
    stride_lab_names = {
        "prod_8": "Canvas Sneakers",
        "prod_11": "Titanium Watch \u2013 Miyota Movement",
        "prod_14": "Stretch Yoga Pants",
        "prod_16": "Performance Running Shorts",
        "prod_20": "Merino Wool Base Layer \u2013 Long Sleeve",
    }

    for prod_id in stride_lab_product_ids:
        product = next((p for p in products if p.get("id") == prod_id), None)
        prod_name = stride_lab_names.get(prod_id, prod_id)
        if product is None:
            return False, f"Product '{prod_name}' (id='{prod_id}') not found in state."
        if product.get("vendor") != "Stride Lab":
            return False, (
                f"Product '{prod_name}' (id='{prod_id}') has vendor '{product.get('vendor')}', "
                f"expected 'Stride Lab'."
            )
        if product.get("status") != "active":
            return False, (
                f"Product '{prod_name}' (id='{prod_id}') has status '{product.get('status')}', "
                f"expected 'active'."
            )
        if product.get("templateId") != no_checkout_id:
            return False, (
                f"Expected product '{prod_name}' (id='{prod_id}') to have "
                f"templateId='{no_checkout_id}' (Product - No checkout buttons), "
                f"but got '{product.get('templateId')}'."
            )

    return True, (
        "All active Stride Lab products (Canvas Sneakers, Titanium Watch, Stretch Yoga Pants, "
        "Performance Running Shorts, Merino Wool Base Layer) assigned to "
        "'Product - No checkout buttons' template."
    )
