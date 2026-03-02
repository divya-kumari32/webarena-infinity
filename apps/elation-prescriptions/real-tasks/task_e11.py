import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that auto-populate last pharmacy setting has been disabled."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    settings = state.get("settings", {})
    auto_populate = settings.get("autoPopulateLastPharmacy")

    if auto_populate is None:
        return False, "settings.autoPopulateLastPharmacy is not present in state"

    if auto_populate is not False:
        return False, (
            f"settings.autoPopulateLastPharmacy is {auto_populate!r}, expected false"
        )

    return True, "Auto-populate last pharmacy setting successfully disabled (autoPopulateLastPharmacy=false)."
