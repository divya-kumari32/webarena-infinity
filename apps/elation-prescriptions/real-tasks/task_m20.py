import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that a med rec was run (lastReconciledDate changed) with no medication list changes."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    current_patient = state.get("currentPatient", {})
    seed_reconciled_date = "2026-01-15T14:30:00Z"

    # Check lastReconciledDate has changed from seed value
    last_reconciled = current_patient.get("lastReconciledDate")
    if last_reconciled is None:
        return False, "currentPatient.lastReconciledDate is not set"

    if last_reconciled == seed_reconciled_date:
        return False, (
            f"currentPatient.lastReconciledDate is still the seed value '{seed_reconciled_date}'. "
            f"Expected it to be updated after running a med rec."
        )

    # Check medication lists remain unchanged
    permanent_rx_meds = state.get("permanentRxMeds", [])
    permanent_otc_meds = state.get("permanentOtcMeds", [])
    temporary_meds = state.get("temporaryMeds", [])

    if len(permanent_rx_meds) != 11:
        return False, (
            f"permanentRxMeds count is {len(permanent_rx_meds)}, expected 11 (no changes). "
            f"Med rec should not have modified the medication lists."
        )

    if len(permanent_otc_meds) != 6:
        return False, (
            f"permanentOtcMeds count is {len(permanent_otc_meds)}, expected 6 (no changes). "
            f"Med rec should not have modified the medication lists."
        )

    if len(temporary_meds) != 3:
        return False, (
            f"temporaryMeds count is {len(temporary_meds)}, expected 3 (no changes). "
            f"Med rec should not have modified the medication lists."
        )

    return True, (
        f"Med rec completed successfully with no medication changes. "
        f"lastReconciledDate updated from '{seed_reconciled_date}' to '{last_reconciled}'. "
        f"permanentRxMeds={len(permanent_rx_meds)}, permanentOtcMeds={len(permanent_otc_meds)}, "
        f"temporaryMeds={len(temporary_meds)}"
    )
