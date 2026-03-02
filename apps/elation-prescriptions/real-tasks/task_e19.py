import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the Atorvastatin to Rosuvastatin change request was approved."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    change_requests = state.get("changeRequests", [])
    target_original = "Atorvastatin 20mg tablet"

    # Find the change request by originalMedication
    cr = None
    for req in change_requests:
        if req.get("originalMedication") == target_original:
            cr = req
            break

    if cr is None:
        return False, (
            f"No change request found with originalMedication='{target_original}'"
        )

    # Check status is approved
    status = cr.get("status")
    if status != "approved":
        return False, (
            f"Change request status is '{status}', expected 'approved'"
        )

    # Check processedBy is set
    processed_by = cr.get("processedBy")
    if not processed_by:
        return False, "Change request processedBy is not set"

    # Check processedDate is set
    processed_date = cr.get("processedDate")
    if not processed_date:
        return False, "Change request processedDate is not set"

    return True, (
        f"Atorvastatin to Rosuvastatin change request approved successfully. "
        f"status='approved', processedBy='{processed_by}', "
        f"processedDate='{processed_date}'."
    )
