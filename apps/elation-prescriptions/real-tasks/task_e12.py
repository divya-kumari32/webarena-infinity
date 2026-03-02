import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that cost estimates display has been hidden."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    settings = state.get("settings", {})
    show_cost = settings.get("showCostEstimates")

    if show_cost is None:
        return False, "settings.showCostEstimates is not present in state"

    if show_cost is not False:
        return False, (
            f"settings.showCostEstimates is {show_cost!r}, expected false"
        )

    return True, "Cost estimates display successfully hidden (showCostEstimates=false)."
