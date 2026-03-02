import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Glucosamine was documented as an OTC med, once daily."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    permanent_otc_meds = state.get("permanentOtcMeds", [])

    # Seed has 6 OTC meds; should now be 7
    if len(permanent_otc_meds) < 7:
        return False, (
            f"Expected at least 7 permanent OTC meds (seed had 6, should have added 1). "
            f"Found {len(permanent_otc_meds)} OTC meds."
        )

    # Find Glucosamine entry (case-insensitive)
    glucosamine_med = None
    for med in permanent_otc_meds:
        name = (med.get("medicationName") or "").lower()
        if "glucosamine" in name:
            glucosamine_med = med
            break

    if glucosamine_med is None:
        med_names = [m.get("medicationName", "") for m in permanent_otc_meds]
        return False, (
            f"No medication containing 'Glucosamine' found in permanentOtcMeds. "
            f"Current OTC meds: {med_names}"
        )

    # Check classification = permanent_otc
    classification = (glucosamine_med.get("classification") or "").lower()
    if classification != "permanent_otc":
        return False, (
            f"Glucosamine classification is '{glucosamine_med.get('classification')}', "
            f"expected 'permanent_otc'"
        )

    # Check sig mentions daily
    sig = (glucosamine_med.get("sig") or "").lower()
    daily_keywords = ["once daily", "daily", "once a day", "every day", "qd"]
    has_daily = any(kw in sig for kw in daily_keywords)
    if not has_daily:
        return False, (
            f"Glucosamine sig does not mention daily dosing. "
            f"sig='{glucosamine_med.get('sig')}'"
        )

    return True, (
        f"Glucosamine OTC documented successfully. "
        f"medicationName='{glucosamine_med.get('medicationName')}', "
        f"classification='{glucosamine_med.get('classification')}', "
        f"sig='{glucosamine_med.get('sig')}', "
        f"total OTC meds={len(permanent_otc_meds)}"
    )
