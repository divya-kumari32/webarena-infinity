import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Montelukast 10mg tablet was moved from permanent Rx to temporary."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    med_name = "Montelukast 10mg tablet"

    # Check that it is no longer in permanentRxMeds
    permanent_rx_meds = state.get("permanentRxMeds", [])
    for med in permanent_rx_meds:
        if med.get("medicationName") == med_name:
            return False, (
                f"'{med_name}' is still present in permanentRxMeds, "
                f"expected it to be moved to temporaryMeds"
            )

    # Check that it is now in temporaryMeds
    temporary_meds = state.get("temporaryMeds", [])
    montelukast = None
    for med in temporary_meds:
        if med.get("medicationName") == med_name:
            montelukast = med
            break

    if montelukast is None:
        return False, (
            f"'{med_name}' was not found in temporaryMeds"
        )

    # Check classification is temporary
    classification = montelukast.get("classification")
    if classification != "temporary":
        return False, (
            f"'{med_name}' classification is '{classification}', "
            f"expected 'temporary'"
        )

    return True, (
        f"'{med_name}' successfully moved from permanent Rx to temporary "
        f"(classification='{classification}')."
    )
