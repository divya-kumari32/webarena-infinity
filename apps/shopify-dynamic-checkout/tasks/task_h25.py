import requests
from collections import Counter


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    products = state.get("products", [])
    themes = state.get("themes", [])
    templates = state.get("templates", [])

    # Find Dawn's 'No checkout buttons' template
    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found."
    no_checkout = next(
        (t for t in templates
         if t.get("themeId") == dawn["id"] and t.get("name") == "Product - No checkout buttons"),
        None
    )
    if no_checkout is None:
        return False, "Template 'Product - No checkout buttons' not found on Dawn."

    # Count active products per vendor
    vendor_counts = Counter(
        p["vendor"] for p in products if p.get("status") == "active"
    )

    # Find vendor(s) with exactly 2 active products
    two_product_vendors = [v for v, c in vendor_counts.items() if c == 2]
    if not two_product_vendors:
        return False, "No vendor with exactly two active products found."

    # Expected: Home & Gather with prod_17 and prod_19
    target_vendor = "Home & Gather"
    if target_vendor not in two_product_vendors:
        return False, f"Expected '{target_vendor}' to have exactly 2 active products."

    # Check both Home & Gather products are on the No checkout buttons template
    vendor_products = [
        p for p in products
        if p.get("vendor") == target_vendor and p.get("status") == "active"
    ]
    for p in vendor_products:
        if p.get("templateId") != no_checkout["id"]:
            return False, (
                f"Product '{p['title']}' (vendor: {target_vendor}) has "
                f"templateId='{p.get('templateId')}', expected '{no_checkout['id']}' "
                f"(No checkout buttons)."
            )

    names = [p["title"] for p in vendor_products]
    return True, (
        f"Vendor '{target_vendor}' (2 active products) — "
        f"{', '.join(names)} moved to 'No checkout buttons' template."
    )
