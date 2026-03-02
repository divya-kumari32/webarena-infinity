import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    templates = state.get("templates", [])

    if not templates:
        return False, "No templates found in state."

    # Check that ALL templates have showAcceleratedCheckout == False
    for tmpl in templates:
        if tmpl.get("showAcceleratedCheckout") is True:
            return False, (
                f"Template '{tmpl.get('name')}' (id='{tmpl.get('id')}', "
                f"themeId='{tmpl.get('themeId')}') still has showAcceleratedCheckout=True."
            )

    return True, (
        "All templates across all themes have showAcceleratedCheckout disabled."
    )
