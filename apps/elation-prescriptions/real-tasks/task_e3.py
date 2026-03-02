import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the pending refill request for Sertraline 50mg tablet was approved."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    # Check refillRequests for Sertraline 50mg tablet
    refill_requests = state.get("refillRequests", [])
    sertraline_refill = None
    for rr in refill_requests:
        if rr.get("medicationName") == "Sertraline 50mg tablet":
            sertraline_refill = rr
            break

    if sertraline_refill is None:
        return False, "No refill request found with medicationName='Sertraline 50mg tablet'"

    # Check status is approved
    status = sertraline_refill.get("status")
    if status != "approved":
        return False, f"Refill request status is '{status}', expected 'approved'"

    # Check processedBy is set
    processed_by = sertraline_refill.get("processedBy")
    if not processed_by:
        return False, "Refill request processedBy is not set"

    # Check processedDate is set
    processed_date = sertraline_refill.get("processedDate")
    if not processed_date:
        return False, "Refill request processedDate is not set"

    # Check linked medication in permanentRxMeds has updated lastPrescribedDate
    permanent_rx_meds = state.get("permanentRxMeds", [])
    sertraline_med = None
    for med in permanent_rx_meds:
        if med.get("medicationName") == "Sertraline 50mg tablet":
            sertraline_med = med
            break

    if sertraline_med is None:
        return False, "No medication found with medicationName='Sertraline 50mg tablet' in permanentRxMeds"

    last_prescribed = sertraline_med.get("lastPrescribedDate")
    if last_prescribed == "2026-01-05":
        return False, "lastPrescribedDate is still the seed value '2026-01-05', expected it to be updated after approval"

    if not last_prescribed:
        return False, "lastPrescribedDate is not set on Sertraline 50mg tablet in permanentRxMeds"

    return True, (
        f"Sertraline 50mg tablet refill request approved successfully. "
        f"processedBy='{processed_by}', processedDate='{processed_date}', "
        f"lastPrescribedDate updated to '{last_prescribed}'"
    )
