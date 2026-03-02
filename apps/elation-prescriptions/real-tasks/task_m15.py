import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the default pharmacy was changed to Walgreens #7892 on Mission St."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    pharmacies = state.get("pharmacies", [])
    settings = state.get("settings", {})

    # Look up Walgreens #7892 by name in the pharmacies list
    walgreens_pharmacy = None
    for pharm in pharmacies:
        name = (pharm.get("name") or "").lower()
        if "walgreens" in name and "7892" in name:
            walgreens_pharmacy = pharm
            break

    if walgreens_pharmacy is None:
        pharm_names = [p.get("name", "") for p in pharmacies]
        return False, (
            f"Could not find Walgreens #7892 in pharmacies list. "
            f"Available pharmacies: {pharm_names}"
        )

    # Verify it's the one on Mission St
    address = (walgreens_pharmacy.get("address") or "").lower()
    if "mission" not in address:
        return False, (
            f"Found Walgreens #7892 but its address is '{walgreens_pharmacy.get('address')}', "
            f"expected it to be on Mission St"
        )

    walgreens_id = walgreens_pharmacy.get("id")

    # Check that settings.defaultPharmacyId matches
    default_pharmacy_id = settings.get("defaultPharmacyId")
    if default_pharmacy_id == "pharm_001":
        return False, (
            f"settings.defaultPharmacyId is still 'pharm_001' (CVS Pharmacy #4521). "
            f"Expected it to be changed to '{walgreens_id}' (Walgreens #7892)"
        )

    if default_pharmacy_id != walgreens_id:
        return False, (
            f"settings.defaultPharmacyId is '{default_pharmacy_id}', "
            f"expected '{walgreens_id}' (Walgreens #7892 at {walgreens_pharmacy.get('address')})"
        )

    return True, (
        f"Default pharmacy changed to Walgreens #7892 successfully. "
        f"defaultPharmacyId='{default_pharmacy_id}', "
        f"pharmacy='{walgreens_pharmacy.get('name')}' at {walgreens_pharmacy.get('address')}"
    )
