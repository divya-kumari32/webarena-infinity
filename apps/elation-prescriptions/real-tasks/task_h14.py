import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that a daily probiotic OTC entry was added to permanentOtcMeds."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    permanent_otc_meds = state.get("permanentOtcMeds", [])

    # Find a probiotic entry (case-insensitive)
    probiotic_med = None
    for med in permanent_otc_meds:
        med_name = (med.get("medicationName") or "").lower()
        if "probiotic" in med_name:
            probiotic_med = med
            break

    if probiotic_med is None:
        med_names = [m.get("medicationName", "") for m in permanent_otc_meds]
        return False, (
            f"No medication containing 'Probiotic' found in permanentOtcMeds. "
            f"Current OTC meds: {med_names}"
        )

    # Check classification is permanent_otc
    classification = probiotic_med.get("classification")
    if classification != "permanent_otc":
        return False, (
            f"Probiotic classification is '{classification}', expected 'permanent_otc'."
        )

    # Check sig mentions daily or food (case-insensitive)
    sig = (probiotic_med.get("sig") or "").lower()
    daily_keywords = ["daily", "once a day", "every day", "food", "qd", "once daily"]
    has_daily = any(kw in sig for kw in daily_keywords)
    if not has_daily:
        return False, (
            f"Probiotic sig does not mention 'daily' or 'food'. "
            f"sig='{probiotic_med.get('sig')}'"
        )

    # Verify count increased from seed (6 -> 7)
    if len(permanent_otc_meds) < 7:
        return False, (
            f"Expected at least 7 permanentOtcMeds after adding Probiotic "
            f"(seed had 6), but found {len(permanent_otc_meds)}."
        )

    return True, (
        f"Probiotic OTC medication added successfully. "
        f"medicationName='{probiotic_med.get('medicationName')}', "
        f"classification='{classification}', sig='{probiotic_med.get('sig')}', "
        f"total OTC meds: {len(permanent_otc_meds)}."
    )
