import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    products = state.get("products", [])
    themes = state.get("themes", [])
    templates = state.get("templates", [])

    # Find Dawn's Gift cards template
    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found."
    gift_cards = next(
        (t for t in templates
         if t.get("themeId") == dawn["id"] and t.get("name") == "Product - Gift cards"),
        None
    )
    if gift_cards is None:
        return False, "Template 'Product - Gift cards' not found on Dawn."

    # Get Atelier Goods products
    atelier = [p for p in products if p.get("vendor") == "Atelier Goods"]
    if not atelier:
        return False, "No Atelier Goods products found."

    # Sort by creation date
    atelier_sorted = sorted(atelier, key=lambda p: p.get("createdAt", ""))
    earliest = atelier_sorted[0]   # Waxed Canvas Backpack (2025-04-08)
    newest = atelier_sorted[-1]    # Cashmere Beanie (2026-01-10)

    # Check newest is active
    if newest.get("status") != "active":
        return False, (
            f"Expected '{newest['title']}' (most recently created Atelier Goods product) "
            f"to be active, but got status='{newest.get('status')}'."
        )

    # Check earliest is on Gift cards template
    if earliest.get("templateId") != gift_cards["id"]:
        return False, (
            f"Expected '{earliest['title']}' (earliest created Atelier Goods product) "
            f"to be on 'Product - Gift cards' template, "
            f"but got templateId='{earliest.get('templateId')}'."
        )

    return True, (
        f"'{newest['title']}' (most recent Atelier Goods) set to active. "
        f"'{earliest['title']}' (earliest Atelier Goods) moved to 'Gift cards' template."
    )
