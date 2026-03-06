import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    inv = next((i for i in state["invoices"] if i["number"] == "INV-0058"), None)
    if not inv:
        return False, "Invoice INV-0058 not found."

    if inv["taxMode"] != "exclusive":
        return False, f"Tax mode is '{inv['taxMode']}', expected 'exclusive'."

    if inv["brandingThemeId"] != "theme_professional":
        return False, f"Branding theme is '{inv['brandingThemeId']}', expected Professional Services."

    return True, "INV-0058 updated to tax-exclusive with Professional Services theme."
