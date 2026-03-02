import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the Gabapentin refill request with 'running low' note was approved."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    refill_requests = state.get("refillRequests", [])

    # Find the refill request whose notes mention "running low" (case-insensitive)
    target_refill = None
    for rr in refill_requests:
        notes = (rr.get("notes") or "").lower()
        if "running low" in notes:
            target_refill = rr
            break

    if target_refill is None:
        # Fallback: look for Gabapentin refill by medication name
        for rr in refill_requests:
            med_name = (rr.get("medicationName") or "").lower()
            if "gabapentin" in med_name:
                target_refill = rr
                break

    if target_refill is None:
        return False, (
            "Could not find the refill request with notes containing 'running low' "
            "or any Gabapentin refill request in refillRequests."
        )

    # Verify it is indeed the Gabapentin refill
    med_name = (target_refill.get("medicationName") or "").lower()
    if "gabapentin" not in med_name:
        return False, (
            f"Refill request with 'running low' note is for '{target_refill.get('medicationName')}', "
            f"expected it to be for Gabapentin."
        )

    # Check status is approved
    status = target_refill.get("status")
    if status != "approved":
        return False, (
            f"Gabapentin refill request (with 'running low' note) status is '{status}', "
            f"expected 'approved'."
        )

    # Check processedBy is set
    processed_by = target_refill.get("processedBy")
    if not processed_by:
        return False, "Gabapentin refill request processedBy is not set."

    # Check processedDate is set
    processed_date = target_refill.get("processedDate")
    if not processed_date:
        return False, "Gabapentin refill request processedDate is not set."

    return True, (
        f"Gabapentin refill request (with 'running low' note) approved successfully. "
        f"processedBy='{processed_by}', processedDate='{processed_date}'."
    )
