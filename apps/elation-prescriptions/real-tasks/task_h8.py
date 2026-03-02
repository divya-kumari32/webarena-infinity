import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Amlodipine 10mg was prescribed for hypertension to the preferred pharmacy."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    permanent_rx_meds = state.get("permanentRxMeds", [])
    current_patient = state.get("currentPatient", {})
    errors = []

    # Get the patient's preferred pharmacy ID
    preferred_pharmacy_id = current_patient.get("preferredPharmacyId", "")
    if not preferred_pharmacy_id:
        errors.append("currentPatient.preferredPharmacyId is not set")

    # Find Amlodipine 10mg entry in permanentRxMeds
    amlodipine_10_med = None
    for med in permanent_rx_meds:
        med_name = med.get("medicationName", "")
        if "Amlodipine" in med_name and "10mg" in med_name:
            amlodipine_10_med = med
            break

    if amlodipine_10_med is None:
        return False, (
            "No medication containing 'Amlodipine' and '10mg' found in permanentRxMeds. "
            "Note: seed has Amlodipine 5mg (prx_006); a new 10mg entry should have been created."
        )

    # Check pharmacyId matches preferred pharmacy
    med_pharmacy_id = amlodipine_10_med.get("pharmacyId", "")
    if preferred_pharmacy_id and med_pharmacy_id != preferred_pharmacy_id:
        errors.append(
            f"Amlodipine 10mg pharmacyId is '{med_pharmacy_id}', "
            f"expected '{preferred_pharmacy_id}' (patient's preferredPharmacyId)"
        )

    # Check diagnosis contains entry with code I10
    diagnosis = amlodipine_10_med.get("diagnosis", [])
    has_hypertension_dx = False
    for dx in diagnosis:
        if dx.get("code") == "I10":
            has_hypertension_dx = True
            break

    if not has_hypertension_dx:
        dx_codes = [dx.get("code", "") for dx in diagnosis]
        errors.append(
            f"Amlodipine 10mg diagnosis does not include code 'I10' (hypertension). "
            f"Found codes: {dx_codes}"
        )

    if errors:
        return False, "Failures: " + "; ".join(errors)

    return True, (
        f"Amlodipine 10mg prescribed for hypertension to preferred pharmacy successfully. "
        f"pharmacyId='{med_pharmacy_id}' matches preferredPharmacyId='{preferred_pharmacy_id}', "
        f"diagnosis includes I10."
    )
