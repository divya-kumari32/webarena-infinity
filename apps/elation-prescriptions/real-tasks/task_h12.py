import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that default pharmacy was switched to UCSF Medical Center Pharmacy."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    # Find the UCSF pharmacy ID by looking up pharmacies by name
    pharmacies = state.get("pharmacies", [])
    ucsf_pharmacy = None
    for pharm in pharmacies:
        name = (pharm.get("name") or "").lower()
        if "ucsf" in name:
            ucsf_pharmacy = pharm
            break

    if ucsf_pharmacy is None:
        return False, (
            "Could not find a pharmacy with 'UCSF' in its name in the pharmacies list. "
            f"Available pharmacies: {[p.get('name') for p in pharmacies]}"
        )

    ucsf_id = ucsf_pharmacy.get("id")

    # Check settings.defaultPharmacyId
    settings = state.get("settings", {})
    default_pharmacy_id = settings.get("defaultPharmacyId")

    if default_pharmacy_id == "pharm_001":
        return False, (
            f"Default pharmacy is still 'pharm_001' (seed value). "
            f"Expected it to be changed to '{ucsf_id}' ({ucsf_pharmacy.get('name')})."
        )

    if default_pharmacy_id != ucsf_id:
        # Try to find the name of the current default pharmacy for a better error message
        current_name = None
        for pharm in pharmacies:
            if pharm.get("id") == default_pharmacy_id:
                current_name = pharm.get("name")
                break
        return False, (
            f"Default pharmacy is '{default_pharmacy_id}' ('{current_name}'), "
            f"expected '{ucsf_id}' ({ucsf_pharmacy.get('name')})."
        )

    return True, (
        f"Default pharmacy successfully changed to '{ucsf_pharmacy.get('name')}' "
        f"(id='{ucsf_id}')."
    )
