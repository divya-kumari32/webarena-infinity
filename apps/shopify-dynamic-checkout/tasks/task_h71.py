import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Disable checkout on Craft/Sense/Ride templates. Craft heading=Inter, Sense heading=Poppins."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    templates = state.get("templates", [])

    craft = next((t for t in themes if t.get("name") == "Craft"), None)
    sense = next((t for t in themes if t.get("name") == "Sense"), None)
    ride = next((t for t in themes if t.get("name") == "Ride"), None)

    if craft is None:
        return False, "Theme 'Craft' not found."
    if sense is None:
        return False, "Theme 'Sense' not found."
    if ride is None:
        return False, "Theme 'Ride' not found."

    # Check all templates for these themes have checkout disabled
    target_theme_ids = {craft["id"], sense["id"], ride["id"]}
    for tmpl in templates:
        if tmpl.get("themeId") in target_theme_ids:
            if tmpl.get("showAcceleratedCheckout") is not False:
                theme_name = next(
                    (t["name"] for t in themes if t["id"] == tmpl["themeId"]), "unknown"
                )
                return False, (f"Expected template '{tmpl['name']}' on {theme_name} "
                              f"to have checkout disabled, got {tmpl.get('showAcceleratedCheckout')}.")

    # Check Craft heading font
    craft_typo = craft.get("settings", {}).get("typography", {})
    if craft_typo.get("headingFont") != "Inter":
        return False, f"Expected Craft heading font 'Inter', got '{craft_typo.get('headingFont')}'."

    # Check Sense heading font
    sense_typo = sense.get("settings", {}).get("typography", {})
    if sense_typo.get("headingFont") != "Poppins":
        return False, f"Expected Sense heading font 'Poppins', got '{sense_typo.get('headingFont')}'."

    return True, ("Checkout disabled on all Craft, Sense, and Ride templates. "
                  "Craft heading: Inter. Sense heading: Poppins.")
