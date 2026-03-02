import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that bulk refill created new Lisinopril and Metformin prescriptions."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    permanent_rx_meds = state.get("permanentRxMeds", [])
    errors = []

    # Seed had 11 permanentRxMeds; after bulk refill should have at least 13
    if len(permanent_rx_meds) < 13:
        errors.append(
            f"permanentRxMeds count is {len(permanent_rx_meds)}, expected at least 13 "
            f"(seed had 11 + 2 new bulk refill entries)"
        )

    # Find all Lisinopril entries
    lisinopril_meds = [
        med for med in permanent_rx_meds
        if "Lisinopril" in med.get("medicationName", "")
    ]

    # Find all Metformin entries
    metformin_meds = [
        med for med in permanent_rx_meds
        if "Metformin" in med.get("medicationName", "")
    ]

    # Check there are new Lisinopril entries (distinct from original prx_001)
    original_lisinopril_ids = {"prx_001"}
    new_lisinopril = [
        med for med in lisinopril_meds
        if med.get("id") not in original_lisinopril_ids
    ]

    if len(new_lisinopril) == 0:
        errors.append(
            "No new Lisinopril entry found in permanentRxMeds distinct from the original (prx_001)"
        )
    else:
        # Check prescriberId is set on new entries
        for med in new_lisinopril:
            if not med.get("prescriberId"):
                errors.append(
                    f"New Lisinopril entry '{med.get('id')}' does not have prescriberId set"
                )

    # Check there are new Metformin entries (distinct from original prx_002)
    original_metformin_ids = {"prx_002"}
    new_metformin = [
        med for med in metformin_meds
        if med.get("id") not in original_metformin_ids
    ]

    if len(new_metformin) == 0:
        errors.append(
            "No new Metformin entry found in permanentRxMeds distinct from the original (prx_002)"
        )
    else:
        # Check prescriberId is set on new entries
        for med in new_metformin:
            if not med.get("prescriberId"):
                errors.append(
                    f"New Metformin entry '{med.get('id')}' does not have prescriberId set"
                )

    if errors:
        return False, "Failures: " + "; ".join(errors)

    return True, (
        f"Bulk refill completed successfully. permanentRxMeds now has {len(permanent_rx_meds)} entries. "
        f"Found {len(new_lisinopril)} new Lisinopril and {len(new_metformin)} new Metformin entries "
        f"with prescriberId set."
    )
