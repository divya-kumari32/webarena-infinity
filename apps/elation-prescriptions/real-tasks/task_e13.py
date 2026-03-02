import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that formulary data display has been turned off."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    settings = state.get("settings", {})
    show_formulary = settings.get("showFormularyData")

    if show_formulary is None:
        return False, "settings.showFormularyData is not present in state"

    if show_formulary is not False:
        return False, (
            f"settings.showFormularyData is {show_formulary!r}, expected false"
        )

    return True, "Formulary data display successfully turned off (showFormularyData=false)."
