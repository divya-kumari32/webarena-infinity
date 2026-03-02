import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that a new sig shortcut was created: 'Take 2 capsules by mouth once daily with breakfast', oral category."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    custom_sigs = state.get("customSigs", [])

    # Seed has 24 sigs; should now be 25
    if len(custom_sigs) < 25:
        return False, (
            f"Expected at least 25 custom sigs (seed had 24, should have added 1). "
            f"Found {len(custom_sigs)} sigs."
        )

    expected_text = "Take 2 capsules by mouth once daily with breakfast"

    # Find the new sig by exact text match
    matching_sig = None
    for sig in custom_sigs:
        sig_text = (sig.get("text") or "").strip()
        if sig_text.lower() == expected_text.lower():
            matching_sig = sig
            break

    if matching_sig is None:
        sig_texts = [s.get("text", "") for s in custom_sigs]
        return False, (
            f"No sig with text '{expected_text}' found. "
            f"Current sigs: {sig_texts}"
        )

    # Check category = oral
    category = (matching_sig.get("category") or "").lower()
    if category != "oral":
        return False, (
            f"Sig category is '{matching_sig.get('category')}', expected 'oral'"
        )

    return True, (
        f"Oral sig shortcut created successfully. "
        f"text='{matching_sig.get('text')}', category='{matching_sig.get('category')}', "
        f"total sigs={len(custom_sigs)}"
    )
