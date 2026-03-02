import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that a patch sig was added: 'Apply 1 patch to skin every 72 hours', topical category."""
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

    expected_text = "Apply 1 patch to skin every 72 hours"

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

    # Check category = topical
    category = (matching_sig.get("category") or "").lower()
    if category != "topical":
        return False, (
            f"Sig category is '{matching_sig.get('category')}', expected 'topical'"
        )

    return True, (
        f"Patch sig added successfully. "
        f"text='{matching_sig.get('text')}', category='{matching_sig.get('category')}', "
        f"total sigs={len(custom_sigs)}"
    )
