import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the Sertraline refill was denied with a follow-up reason."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    errors = []

    # Find the Sertraline refill request
    refill_requests = state.get("refillRequests", [])
    sertraline_refill = None
    for rr in refill_requests:
        med_name = rr.get("medicationName", "")
        if "sertraline" in med_name.lower():
            sertraline_refill = rr
            break

    if sertraline_refill is None:
        return False, "No refill request found for Sertraline."

    # Check status is denied
    status = sertraline_refill.get("status")
    if status != "denied":
        errors.append(f"Refill request status is '{status}', expected 'denied'")

    # Check processedBy is set
    processed_by = sertraline_refill.get("processedBy")
    if not processed_by:
        errors.append("Refill request processedBy is not set")

    # Check processedDate is set
    processed_date = sertraline_refill.get("processedDate")
    if not processed_date:
        errors.append("Refill request processedDate is not set")

    # Check denyReason is set and mentions follow-up
    deny_reason = sertraline_refill.get("denyReason", "")
    if not deny_reason:
        errors.append("Refill request denyReason is not set")
    elif "follow" not in deny_reason.lower() and "appointment" not in deny_reason.lower():
        errors.append(
            f"denyReason is '{deny_reason}', expected it to mention follow-up or appointment"
        )

    if errors:
        return False, f"Sertraline refill denial issues: {'; '.join(errors)}"

    return True, (
        f"Sertraline refill denied successfully. "
        f"Status='denied', processedBy='{processed_by}', "
        f"denyReason='{deny_reason}'."
    )
