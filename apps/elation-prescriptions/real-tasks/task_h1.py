import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Lisinopril and Omeprazole refills were approved and Atorvastatin was denied."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    refill_requests = state.get("refillRequests", [])
    permanent_rx_meds = state.get("permanentRxMeds", [])
    errors = []

    # --- (a) Lisinopril refill approved ---
    lisinopril_refill = None
    for rr in refill_requests:
        if "Lisinopril" in rr.get("medicationName", ""):
            lisinopril_refill = rr
            break

    if lisinopril_refill is None:
        errors.append("No refill request found containing 'Lisinopril'")
    else:
        if lisinopril_refill.get("status") != "approved":
            errors.append(
                f"Lisinopril refill status is '{lisinopril_refill.get('status')}', expected 'approved'"
            )
        if not lisinopril_refill.get("processedBy"):
            errors.append("Lisinopril refill processedBy is not set")
        if not lisinopril_refill.get("processedDate"):
            errors.append("Lisinopril refill processedDate is not set")

    # Check Lisinopril med lastPrescribedDate updated
    lisinopril_med = None
    for med in permanent_rx_meds:
        if "Lisinopril" in med.get("medicationName", ""):
            lisinopril_med = med
            break

    if lisinopril_med is None:
        errors.append("No medication containing 'Lisinopril' found in permanentRxMeds")
    else:
        lpd = lisinopril_med.get("lastPrescribedDate", "")
        if lpd == "2025-12-15":
            errors.append(
                "Lisinopril lastPrescribedDate is still '2025-12-15', expected it to be updated after approval"
            )
        if not lpd:
            errors.append("Lisinopril lastPrescribedDate is not set")

    # --- (b) Omeprazole refill approved ---
    omeprazole_refill = None
    for rr in refill_requests:
        if "Omeprazole" in rr.get("medicationName", ""):
            omeprazole_refill = rr
            break

    if omeprazole_refill is None:
        errors.append("No refill request found containing 'Omeprazole'")
    else:
        if omeprazole_refill.get("status") != "approved":
            errors.append(
                f"Omeprazole refill status is '{omeprazole_refill.get('status')}', expected 'approved'"
            )
        if not omeprazole_refill.get("processedBy"):
            errors.append("Omeprazole refill processedBy is not set")
        if not omeprazole_refill.get("processedDate"):
            errors.append("Omeprazole refill processedDate is not set")

    # Check Omeprazole med lastPrescribedDate updated
    omeprazole_med = None
    for med in permanent_rx_meds:
        if "Omeprazole" in med.get("medicationName", ""):
            omeprazole_med = med
            break

    if omeprazole_med is None:
        errors.append("No medication containing 'Omeprazole' found in permanentRxMeds")
    else:
        lpd = omeprazole_med.get("lastPrescribedDate", "")
        if lpd == "2025-10-08":
            errors.append(
                "Omeprazole lastPrescribedDate is still '2025-10-08', expected it to be updated after approval"
            )
        if not lpd:
            errors.append("Omeprazole lastPrescribedDate is not set")

    # --- (c) Atorvastatin refill denied ---
    atorvastatin_refill = None
    for rr in refill_requests:
        if "Atorvastatin" in rr.get("medicationName", ""):
            atorvastatin_refill = rr
            break

    if atorvastatin_refill is None:
        errors.append("No refill request found containing 'Atorvastatin'")
    else:
        if atorvastatin_refill.get("status") != "denied":
            errors.append(
                f"Atorvastatin refill status is '{atorvastatin_refill.get('status')}', expected 'denied'"
            )
        if not atorvastatin_refill.get("processedBy"):
            errors.append("Atorvastatin refill processedBy is not set")
        if not atorvastatin_refill.get("processedDate"):
            errors.append("Atorvastatin refill processedDate is not set")
        if not atorvastatin_refill.get("denyReason"):
            errors.append("Atorvastatin refill denyReason is not set")

    if errors:
        return False, "Failures: " + "; ".join(errors)

    return True, (
        "All three refill actions completed successfully. "
        "Lisinopril approved (lastPrescribedDate updated), "
        "Omeprazole approved (lastPrescribedDate updated), "
        "Atorvastatin denied with reason set."
    )
