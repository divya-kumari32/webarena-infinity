import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the Gabapentin sig clarification change request was denied."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    change_requests = state.get("changeRequests", [])
    target_med = "Gabapentin 300mg capsule"

    # Find the change request by medicationName
    cr = None
    for req in change_requests:
        if req.get("medicationName") == target_med:
            cr = req
            break

    if cr is None:
        return False, (
            f"No change request found with medicationName='{target_med}'"
        )

    # Check status is denied
    status = cr.get("status")
    if status != "denied":
        return False, (
            f"Change request status is '{status}', expected 'denied'"
        )

    # Check processedBy is set
    processed_by = cr.get("processedBy")
    if not processed_by:
        return False, "Change request processedBy is not set"

    # Check processedDate is set
    processed_date = cr.get("processedDate")
    if not processed_date:
        return False, "Change request processedDate is not set"

    # Check denyReason is set and non-empty
    deny_reason = cr.get("denyReason")
    if not deny_reason or not str(deny_reason).strip():
        return False, (
            f"Change request denyReason is not set or empty "
            f"(denyReason={deny_reason!r})"
        )

    return True, (
        f"Gabapentin sig clarification change request denied successfully. "
        f"status='denied', processedBy='{processed_by}', "
        f"processedDate='{processed_date}', denyReason='{deny_reason}'."
    )
