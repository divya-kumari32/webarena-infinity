import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Gift cards template: checkout enabled + 'Send as gift'. Dawn colors: #059669/#FFFFFF."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    templates = state.get("templates", [])

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

    # Check template settings
    if gift_cards.get("showAcceleratedCheckout") is not True:
        return False, (f"Expected 'Gift cards' checkout enabled, "
                      f"got {gift_cards.get('showAcceleratedCheckout')}.")

    if gift_cards.get("buyButtonText") != "Send as gift":
        return False, (f"Expected buy button text 'Send as gift', "
                      f"got '{gift_cards.get('buyButtonText')}'.")

    # Check Dawn colors
    dawn_colors = dawn.get("settings", {}).get("colors", {})

    actual_bg = dawn_colors.get("accentButtonBg", "")
    if actual_bg.upper() != "#059669":
        return False, f"Expected accent button bg '#059669', got '{actual_bg}'."

    actual_text = dawn_colors.get("accentButtonText", "")
    if actual_text.upper() != "#FFFFFF":
        return False, f"Expected accent button text '#FFFFFF', got '{actual_text}'."

    return True, ("Gift cards template: checkout enabled, buy text 'Send as gift'. "
                  "Dawn button colors: #059669/#FFFFFF.")
