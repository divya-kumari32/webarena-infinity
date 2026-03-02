import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the pending refill request for Omeprazole 20mg capsule was approved."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    # Check refillRequests for Omeprazole 20mg capsule
    refill_requests = state.get("refillRequests", [])
    omeprazole_refill = None
    for rr in refill_requests:
        if rr.get("medicationName") == "Omeprazole 20mg capsule":
            omeprazole_refill = rr
            break

    if omeprazole_refill is None:
        return False, "No refill request found with medicationName='Omeprazole 20mg capsule'"

    # Check status is approved
    status = omeprazole_refill.get("status")
    if status != "approved":
        return False, f"Refill request status is '{status}', expected 'approved'"

    # Check processedBy is set
    processed_by = omeprazole_refill.get("processedBy")
    if not processed_by:
        return False, "Refill request processedBy is not set"

    # Check processedDate is set
    processed_date = omeprazole_refill.get("processedDate")
    if not processed_date:
        return False, "Refill request processedDate is not set"

    # Check linked medication in permanentRxMeds has updated lastPrescribedDate
    permanent_rx_meds = state.get("permanentRxMeds", [])
    omeprazole_med = None
    for med in permanent_rx_meds:
        if med.get("medicationName") == "Omeprazole 20mg capsule":
            omeprazole_med = med
            break

    if omeprazole_med is None:
        return False, "No medication found with medicationName='Omeprazole 20mg capsule' in permanentRxMeds"

    last_prescribed = omeprazole_med.get("lastPrescribedDate")
    if last_prescribed == "2025-10-08":
        return False, "lastPrescribedDate is still the seed value '2025-10-08', expected it to be updated after approval"

    if not last_prescribed:
        return False, "lastPrescribedDate is not set on Omeprazole 20mg capsule in permanentRxMeds"

    return True, (
        f"Omeprazole 20mg capsule refill request approved successfully. "
        f"processedBy='{processed_by}', processedDate='{processed_date}', "
        f"lastPrescribedDate updated to '{last_prescribed}'"
    )
