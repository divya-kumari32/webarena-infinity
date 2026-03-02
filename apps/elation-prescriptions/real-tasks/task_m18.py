import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the sublingual sig was updated from the old text to the new longer text."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    custom_sigs = state.get("customSigs", [])

    old_text = "Dissolve 1 tablet under the tongue as needed"
    new_text = "Dissolve 1 tablet under the tongue every 5 minutes as needed, max 3 doses"

    # Check the old text no longer exists
    for sig in custom_sigs:
        sig_text = (sig.get("text") or "").strip()
        if sig_text.lower() == old_text.lower():
            return False, (
                f"Old sublingual sig text still exists: '{sig_text}'. "
                f"Expected it to be updated to: '{new_text}'"
            )

    # Check the new text exists
    matching_sig = None
    for sig in custom_sigs:
        sig_text = (sig.get("text") or "").strip()
        if sig_text.lower() == new_text.lower():
            matching_sig = sig
            break

    if matching_sig is None:
        sig_texts = [s.get("text", "") for s in custom_sigs]
        return False, (
            f"New sublingual sig text '{new_text}' not found. "
            f"Current sigs: {sig_texts}"
        )

    return True, (
        f"Sublingual sig updated successfully. "
        f"text='{matching_sig.get('text')}', category='{matching_sig.get('category')}'"
    )
