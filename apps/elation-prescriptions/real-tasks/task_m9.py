import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Levothyroxine 50mcg was prescribed as a permanent Rx to CVS."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    errors = []

    # Find Levothyroxine 50mcg in permanentRxMeds
    permanent_rx_meds = state.get("permanentRxMeds", [])
    levo_match = [
        m for m in permanent_rx_meds
        if "levothyroxine" in m.get("medicationName", "").lower()
        and "50" in m.get("medicationName", "")
    ]

    if not levo_match:
        return False, (
            "No medication found in permanentRxMeds containing 'Levothyroxine' and '50'. "
            f"permanentRxMeds count: {len(permanent_rx_meds)}"
        )

    med = levo_match[0]

    # Check classification is permanent_rx
    classification = med.get("classification")
    if classification != "permanent_rx":
        errors.append(
            f"classification is '{classification}', expected 'permanent_rx'"
        )

    # Check pharmacy contains CVS
    pharmacy_name = med.get("pharmacyName", "")
    if "cvs" not in pharmacy_name.lower():
        errors.append(
            f"pharmacyName is '{pharmacy_name}', expected it to contain 'CVS'"
        )

    # Check sig mentions daily
    sig = med.get("sig", "")
    if "daily" not in sig.lower():
        errors.append(
            f"sig is '{sig}', expected it to mention 'daily'"
        )

    # Seed has 11 permanentRxMeds, should now have 12
    if len(permanent_rx_meds) != 12:
        errors.append(
            f"Expected 12 permanentRxMeds after adding Levothyroxine (seed had 11), "
            f"found {len(permanent_rx_meds)}"
        )

    if errors:
        return False, f"Levothyroxine prescription issues: {'; '.join(errors)}"

    return True, (
        f"Levothyroxine 50mcg successfully prescribed as permanent Rx to CVS. "
        f"pharmacyName='{pharmacy_name}', sig='{sig}', classification='permanent_rx', "
        f"permanentRxMeds count=12."
    )
