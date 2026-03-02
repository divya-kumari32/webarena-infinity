import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the Metoprolol refill was approved with 3 refills."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    errors = []

    # Find the Metoprolol refill request
    refill_requests = state.get("refillRequests", [])
    metoprolol_refill = None
    for rr in refill_requests:
        med_name = rr.get("medicationName", "")
        if "metoprolol" in med_name.lower():
            metoprolol_refill = rr
            break

    if metoprolol_refill is None:
        return False, "No refill request found for Metoprolol."

    # Check status is approved
    status = metoprolol_refill.get("status")
    if status != "approved":
        errors.append(f"Refill request status is '{status}', expected 'approved'")

    # Check processedBy is set
    processed_by = metoprolol_refill.get("processedBy")
    if not processed_by:
        errors.append("Refill request processedBy is not set")

    # Check processedDate is set
    processed_date = metoprolol_refill.get("processedDate")
    if not processed_date:
        errors.append("Refill request processedDate is not set")

    # Check modifications.refills = 3
    modifications = metoprolol_refill.get("modifications", {})
    if not modifications:
        errors.append("Refill request has no modifications recorded")
    else:
        mod_refills = modifications.get("refills")
        if mod_refills != 3:
            errors.append(
                f"Refill modifications refills is {mod_refills}, expected 3"
            )

    # Find the Metoprolol medication in permanentRxMeds
    permanent_rx_meds = state.get("permanentRxMeds", [])
    metoprolol_med = None
    for med in permanent_rx_meds:
        med_name = med.get("medicationName", "")
        if "metoprolol" in med_name.lower():
            metoprolol_med = med
            break

    if metoprolol_med is None:
        errors.append("Metoprolol not found in permanentRxMeds")
    else:
        # Check refillsRemaining is 3
        refills_remaining = metoprolol_med.get("refillsRemaining")
        if refills_remaining != 3:
            errors.append(
                f"Metoprolol refillsRemaining is {refills_remaining}, expected 3"
            )

        # Check lastPrescribedDate updated from seed value "2025-11-20"
        last_prescribed = metoprolol_med.get("lastPrescribedDate")
        if last_prescribed == "2025-11-20":
            errors.append(
                "lastPrescribedDate is still the seed value '2025-11-20', expected it to be updated"
            )
        if not last_prescribed:
            errors.append("lastPrescribedDate is not set on Metoprolol in permanentRxMeds")

    if errors:
        return False, f"Metoprolol refill approval issues: {'; '.join(errors)}"

    return True, (
        f"Metoprolol refill approved with 3 refills. "
        f"Refill status='approved', processedBy='{processed_by}', "
        f"refillsRemaining=3, lastPrescribedDate updated."
    )
