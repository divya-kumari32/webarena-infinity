import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Amoxicillin 500mg capsule was moved from temporary to permanent Rx."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    med_name = "Amoxicillin 500mg capsule"

    # Check that it is no longer in temporaryMeds
    temporary_meds = state.get("temporaryMeds", [])
    for med in temporary_meds:
        if med.get("medicationName") == med_name:
            return False, (
                f"'{med_name}' is still present in temporaryMeds, "
                f"expected it to be moved to permanentRxMeds"
            )

    # Check that it is now in permanentRxMeds
    permanent_rx_meds = state.get("permanentRxMeds", [])
    amoxicillin = None
    for med in permanent_rx_meds:
        if med.get("medicationName") == med_name:
            amoxicillin = med
            break

    if amoxicillin is None:
        return False, (
            f"'{med_name}' was not found in permanentRxMeds"
        )

    # Check classification is permanent_rx
    classification = amoxicillin.get("classification")
    if classification != "permanent_rx":
        return False, (
            f"'{med_name}' classification is '{classification}', "
            f"expected 'permanent_rx'"
        )

    return True, (
        f"'{med_name}' successfully reclassified from temporary to permanent Rx "
        f"(classification='{classification}')."
    )
