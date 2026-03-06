import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Cascade Software repeating invoice is rep_003
    ri = next((r for r in state["repeatingInvoices"] if r["id"] == "rep_003"), None)
    if not ri:
        return False, "Cascade Software repeating invoice (rep_003) not found."

    if ri["frequency"] != "fortnightly":
        return False, f"Frequency is '{ri['frequency']}', expected 'fortnightly'."

    if ri["brandingThemeId"] != "theme_professional":
        return False, f"Branding theme is '{ri['brandingThemeId']}', expected Professional Services."

    return True, "Cascade Software repeating invoice changed to fortnightly with Professional Services."
