import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])

    # Find Craft theme
    craft = next((t for t in themes if t.get("name") == "Craft"), None)
    if craft is None:
        return False, "Theme 'Craft' not found."

    # Check Craft is published
    if craft.get("role") != "main":
        return False, f"Expected Craft to be published (role='main'), but got role='{craft.get('role')}'."

    # Check typography
    typo = craft.get("settings", {}).get("typography", {})

    if typo.get("headingFont") != "Oswald":
        return False, (
            f"Expected Craft headingFont to be 'Oswald', "
            f"but got '{typo.get('headingFont')}'."
        )

    if typo.get("bodyFont") != "Nunito":
        return False, (
            f"Expected Craft bodyFont to be 'Nunito', "
            f"but got '{typo.get('bodyFont')}'."
        )

    return True, (
        "Craft theme published with heading font 'Oswald' and body font 'Nunito'."
    )
