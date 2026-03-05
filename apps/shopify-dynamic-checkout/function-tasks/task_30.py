import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that an alternate template 'Product - Express Checkout' exists on the Craft theme."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    craft = next((t for t in themes if t["name"] == "Craft"), None)
    if not craft:
        return False, "Theme 'Craft' not found."

    templates = state.get("templates", [])
    template = next(
        (t for t in templates if t["name"] == "Product - Express Checkout" and t["themeId"] == craft["id"]),
        None,
    )
    if not template:
        return False, "Template 'Product - Express Checkout' for Craft theme not found."

    if template.get("isAlternate") is not True:
        return False, f"Expected template to be an alternate template (isAlternate=true), got '{template.get('isAlternate')}'."

    if template.get("isDefault") is not False:
        return False, f"Expected template to not be default (isDefault=false), got '{template.get('isDefault')}'."

    return True, "Alternate template 'Product - Express Checkout' exists on the Craft theme with correct properties."
