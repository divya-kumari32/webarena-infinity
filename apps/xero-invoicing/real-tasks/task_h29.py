import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # TechVault's highest-value invoice is INV-0055 ($41,800)
    inv = next((i for i in state["invoices"] if i["number"] == "INV-0055"), None)
    if not inv:
        return False, "Invoice INV-0055 not found."

    if inv["brandingThemeId"] != "theme_retail":
        return False, f"Branding theme is '{inv['brandingThemeId']}', expected 'theme_retail' (Retail)."

    if inv.get("title") != "Q1 2026 Major Project":
        return False, f"Title is '{inv.get('title')}', expected 'Q1 2026 Major Project'."

    return True, "INV-0055 updated with Retail theme and title 'Q1 2026 Major Project'."
