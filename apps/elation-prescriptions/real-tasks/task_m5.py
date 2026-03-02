import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Omeprazole was discontinued (switching to famotidine)."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    errors = []

    # Check that Omeprazole is NOT in permanentRxMeds
    permanent_rx_meds = state.get("permanentRxMeds", [])
    omeprazole_active = [
        m for m in permanent_rx_meds
        if "omeprazole" in m.get("medicationName", "").lower()
    ]
    if omeprazole_active:
        errors.append("Omeprazole is still in permanentRxMeds; expected it to be discontinued")

    # Check that Omeprazole IS in discontinuedMeds
    discontinued_meds = state.get("discontinuedMeds", [])
    omeprazole_disc = [
        m for m in discontinued_meds
        if "omeprazole" in m.get("medicationName", "").lower()
    ]
    if not omeprazole_disc:
        errors.append("Omeprazole not found in discontinuedMeds")
    else:
        med = omeprazole_disc[0]

        # Check status is discontinued
        status = med.get("status")
        if status != "discontinued":
            errors.append(
                f"Omeprazole in discontinuedMeds has status '{status}', expected 'discontinued'"
            )

        # Check discontinuedDate is set
        disc_date = med.get("discontinuedDate")
        if not disc_date:
            errors.append("Omeprazole discontinuedDate is not set")

        # Check discontinuedBy is set
        disc_by = med.get("discontinuedBy")
        if not disc_by:
            errors.append("Omeprazole discontinuedBy is not set")

        # Check discontinueReason is set
        disc_reason = med.get("discontinueReason")
        if not disc_reason:
            errors.append("Omeprazole discontinueReason is not set")

    # Seed has 6 discontinued meds; should now have 7
    if len(discontinued_meds) < 7:
        errors.append(
            f"Expected at least 7 discontinuedMeds (seed had 6), found {len(discontinued_meds)}"
        )

    if errors:
        return False, f"Omeprazole discontinuation issues: {'; '.join(errors)}"

    return True, (
        "Omeprazole successfully discontinued. "
        "Removed from permanentRxMeds, added to discontinuedMeds with "
        f"status='discontinued', discontinuedDate set, discontinuedBy set, reason set."
    )
