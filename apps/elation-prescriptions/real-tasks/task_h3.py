import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that medication reconciliation was performed and low-dose Aspirin was discontinued."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    current_patient = state.get("currentPatient", {})
    permanent_otc_meds = state.get("permanentOtcMeds", [])
    discontinued_meds = state.get("discontinuedMeds", [])
    errors = []

    # Check lastReconciledDate was updated from seed value
    last_reconciled = current_patient.get("lastReconciledDate", "")
    if last_reconciled == "2026-01-15T14:30:00Z":
        errors.append(
            "lastReconciledDate is still the seed value '2026-01-15T14:30:00Z', "
            "expected it to be updated after reconciliation"
        )
    if not last_reconciled:
        errors.append("lastReconciledDate is not set on currentPatient")

    # Check Aspirin 81mg is NOT in permanentOtcMeds
    for med in permanent_otc_meds:
        med_name = med.get("medicationName", "")
        if "Aspirin" in med_name and "81mg" in med_name:
            errors.append(
                f"Aspirin 81mg still found in permanentOtcMeds: '{med_name}'"
            )
            break

    # Check Aspirin 81mg IS in discontinuedMeds
    aspirin_discontinued = None
    for med in discontinued_meds:
        med_name = med.get("medicationName", "")
        if "Aspirin" in med_name and "81mg" in med_name:
            aspirin_discontinued = med
            break

    if aspirin_discontinued is None:
        errors.append(
            "Aspirin 81mg not found in discontinuedMeds after discontinuation"
        )

    if errors:
        return False, "Failures: " + "; ".join(errors)

    return True, (
        "Medication reconciliation completed and Aspirin 81mg discontinued successfully. "
        f"lastReconciledDate updated to '{last_reconciled}', "
        f"Aspirin removed from permanentOtcMeds and added to discontinuedMeds."
    )
