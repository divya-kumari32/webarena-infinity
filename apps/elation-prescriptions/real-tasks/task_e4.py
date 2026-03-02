import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the pending refill request for Atorvastatin 20mg tablet was denied with a reason."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    # Check refillRequests for Atorvastatin 20mg tablet
    refill_requests = state.get("refillRequests", [])
    atorvastatin_refill = None
    for rr in refill_requests:
        if rr.get("medicationName") == "Atorvastatin 20mg tablet":
            atorvastatin_refill = rr
            break

    if atorvastatin_refill is None:
        return False, "No refill request found with medicationName='Atorvastatin 20mg tablet'"

    # Check status is denied
    status = atorvastatin_refill.get("status")
    if status != "denied":
        return False, f"Refill request status is '{status}', expected 'denied'"

    # Check processedBy is set
    processed_by = atorvastatin_refill.get("processedBy")
    if not processed_by:
        return False, "Refill request processedBy is not set"

    # Check processedDate is set
    processed_date = atorvastatin_refill.get("processedDate")
    if not processed_date:
        return False, "Refill request processedDate is not set"

    # Check denyReason is set and non-empty
    deny_reason = atorvastatin_refill.get("denyReason", "")
    if not deny_reason or not deny_reason.strip():
        return False, "Refill request denyReason is not set or is empty"

    return True, (
        f"Atorvastatin 20mg tablet refill request denied successfully. "
        f"processedBy='{processed_by}', processedDate='{processed_date}', "
        f"denyReason='{deny_reason}'"
    )
