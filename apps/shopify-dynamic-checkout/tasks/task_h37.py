import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    templates = state.get("templates", [])

    # Find Craft theme
    craft = next((t for t in themes if t.get("name") == "Craft"), None)
    if craft is None:
        return False, "Theme 'Craft' not found."

    # Check Craft is published
    if craft.get("role") != "main":
        return False, f"Expected Craft to be published (role='main'), but got role='{craft.get('role')}'."

    # Find Featured template on Craft
    featured = next(
        (t for t in templates
         if t.get("themeId") == craft["id"] and t.get("name") == "Product - Featured"),
        None
    )
    if featured is None:
        return False, "Template 'Product - Featured' not found on Craft."

    # Check checkout disabled on Featured
    if featured.get("showAcceleratedCheckout") is not False:
        return False, (
            f"Expected 'Product - Featured' template to have showAcceleratedCheckout=False, "
            f"but got {featured.get('showAcceleratedCheckout')}."
        )

    # Check button font
    typo = craft.get("settings", {}).get("typography", {})
    if typo.get("buttonFont") != "Montserrat":
        return False, (
            f"Expected Craft buttonFont to be 'Montserrat', "
            f"but got '{typo.get('buttonFont')}'."
        )

    return True, (
        "Craft published, 'Product - Featured' checkout disabled, "
        "button font set to Montserrat."
    )
