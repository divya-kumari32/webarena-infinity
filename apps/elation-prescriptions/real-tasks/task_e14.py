import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the injectable sig shortcut has been deleted."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    custom_sigs = state.get("customSigs", [])
    target_text = "Inject subcutaneously once weekly"

    for sig in custom_sigs:
        if sig.get("text") == target_text:
            return False, (
                f"Custom sig with text '{target_text}' still exists "
                f"(id='{sig.get('id')}'), expected it to be deleted"
            )

    sig_count = len(custom_sigs)
    if sig_count != 23:
        return False, (
            f"Expected 23 custom sigs after deletion (seed had 24), "
            f"but found {sig_count}"
        )

    return True, (
        f"Injectable sig shortcut '{target_text}' successfully deleted. "
        f"Custom sigs count is now {sig_count}."
    )
