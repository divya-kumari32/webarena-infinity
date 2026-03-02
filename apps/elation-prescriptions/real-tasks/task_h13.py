import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the medication swap change request was approved and the sig clarification remains pending."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    change_requests = state.get("changeRequests", [])

    # Identify the swap request: originalMedication != requestedMedication
    swap_request = None
    clarification_request = None

    for cr in change_requests:
        original = (cr.get("originalMedication") or "").lower().strip()
        requested = (cr.get("requestedMedication") or "").lower().strip()
        if original and requested and original != requested:
            swap_request = cr
        elif original and requested and original == requested:
            clarification_request = cr

    if swap_request is None:
        return False, (
            "Could not find a change request where originalMedication differs from requestedMedication. "
            f"Change requests: {[(cr.get('id'), cr.get('originalMedication'), cr.get('requestedMedication')) for cr in change_requests]}"
        )

    # Check swap request is approved
    swap_status = swap_request.get("status")
    if swap_status != "approved":
        return False, (
            f"Medication swap change request (id='{swap_request.get('id')}', "
            f"{swap_request.get('originalMedication')} -> {swap_request.get('requestedMedication')}) "
            f"status is '{swap_status}', expected 'approved'."
        )

    # Check processedBy is set
    processed_by = swap_request.get("processedBy")
    if not processed_by:
        return False, "Medication swap change request processedBy is not set."

    # Check processedDate is set
    processed_date = swap_request.get("processedDate")
    if not processed_date:
        return False, "Medication swap change request processedDate is not set."

    # Check the clarification request is still pending
    if clarification_request is not None:
        clar_status = clarification_request.get("status")
        if clar_status != "pending":
            return False, (
                f"Sig clarification change request (id='{clarification_request.get('id')}') "
                f"status is '{clar_status}', expected it to remain 'pending'. "
                f"Only the medication swap should have been approved."
            )

    return True, (
        f"Medication swap change request approved successfully. "
        f"id='{swap_request.get('id')}', "
        f"{swap_request.get('originalMedication')} -> {swap_request.get('requestedMedication')}, "
        f"processedBy='{processed_by}', processedDate='{processed_date}'."
    )
