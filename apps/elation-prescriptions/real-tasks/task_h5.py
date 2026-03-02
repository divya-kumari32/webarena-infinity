import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Albuterol inhaler was prescribed to CVS with diagnosis J45.20."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    permanent_rx_meds = state.get("permanentRxMeds", [])
    errors = []

    # Find Albuterol entry in permanentRxMeds
    albuterol_med = None
    for med in permanent_rx_meds:
        if "Albuterol" in med.get("medicationName", ""):
            albuterol_med = med
            break

    if albuterol_med is None:
        return False, "No medication containing 'Albuterol' found in permanentRxMeds"

    # Check pharmacy contains CVS
    pharmacy_name = albuterol_med.get("pharmacyName", "")
    if "CVS" not in pharmacy_name:
        errors.append(
            f"Albuterol pharmacyName is '{pharmacy_name}', expected it to contain 'CVS'"
        )

    # Check diagnosis array has entry with code J45.20
    diagnosis = albuterol_med.get("diagnosis", [])
    has_asthma_dx = False
    for dx in diagnosis:
        if dx.get("code") == "J45.20":
            has_asthma_dx = True
            break

    if not has_asthma_dx:
        dx_codes = [dx.get("code", "") for dx in diagnosis]
        errors.append(
            f"Albuterol diagnosis does not include code 'J45.20'. Found codes: {dx_codes}"
        )

    # Check unit is inhalers
    unit = albuterol_med.get("unit", "")
    if unit.lower() != "inhalers":
        errors.append(
            f"Albuterol unit is '{unit}', expected 'inhalers'"
        )

    if errors:
        return False, "Failures: " + "; ".join(errors)

    return True, (
        f"Albuterol inhaler prescribed successfully. "
        f"Pharmacy: '{pharmacy_name}', diagnosis includes J45.20, "
        f"unit='{unit}'."
    )
