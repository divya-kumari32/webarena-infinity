import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify all pending CVS refills approved except Atorvastatin (denied with reason)."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    refill_requests = state.get("refillRequests", [])

    errors = []

    # Build lookup by medication name (case-insensitive)
    def find_refill(name_fragment):
        for rr in refill_requests:
            med_name = (rr.get("medicationName") or "").lower()
            if name_fragment.lower() in med_name:
                # Only match CVS pharmacy refills
                pharmacy = (rr.get("pharmacyName") or "").lower()
                if "cvs" in pharmacy:
                    return rr
        return None

    # (a) Lisinopril refill should be approved
    lisinopril_rr = find_refill("lisinopril")
    if lisinopril_rr is None:
        errors.append("Could not find Lisinopril CVS refill request.")
    else:
        if lisinopril_rr.get("status") != "approved":
            errors.append(
                f"Lisinopril refill status is '{lisinopril_rr.get('status')}', expected 'approved'."
            )
        if not lisinopril_rr.get("processedBy"):
            errors.append("Lisinopril refill processedBy is not set.")
        if not lisinopril_rr.get("processedDate"):
            errors.append("Lisinopril refill processedDate is not set.")

    # (b) Atorvastatin refill should be denied with reason
    atorvastatin_rr = find_refill("atorvastatin")
    if atorvastatin_rr is None:
        errors.append("Could not find Atorvastatin CVS refill request.")
    else:
        if atorvastatin_rr.get("status") != "denied":
            errors.append(
                f"Atorvastatin refill status is '{atorvastatin_rr.get('status')}', expected 'denied'."
            )
        deny_reason = atorvastatin_rr.get("denyReason") or atorvastatin_rr.get("denialReason") or ""
        if not deny_reason:
            errors.append(
                "Atorvastatin refill denyReason is not set. Expected a denial reason."
            )

    # (c) Gabapentin refill should be approved
    gabapentin_rr = find_refill("gabapentin")
    if gabapentin_rr is None:
        errors.append("Could not find Gabapentin CVS refill request.")
    else:
        if gabapentin_rr.get("status") != "approved":
            errors.append(
                f"Gabapentin refill status is '{gabapentin_rr.get('status')}', expected 'approved'."
            )
        if not gabapentin_rr.get("processedBy"):
            errors.append("Gabapentin refill processedBy is not set.")
        if not gabapentin_rr.get("processedDate"):
            errors.append("Gabapentin refill processedDate is not set.")

    # (d) Omeprazole refill should be approved
    omeprazole_rr = find_refill("omeprazole")
    if omeprazole_rr is None:
        errors.append("Could not find Omeprazole CVS refill request.")
    else:
        if omeprazole_rr.get("status") != "approved":
            errors.append(
                f"Omeprazole refill status is '{omeprazole_rr.get('status')}', expected 'approved'."
            )
        if not omeprazole_rr.get("processedBy"):
            errors.append("Omeprazole refill processedBy is not set.")
        if not omeprazole_rr.get("processedDate"):
            errors.append("Omeprazole refill processedDate is not set.")

    # (e) Metoprolol refill should be approved
    metoprolol_rr = find_refill("metoprolol")
    if metoprolol_rr is None:
        errors.append("Could not find Metoprolol CVS refill request.")
    else:
        if metoprolol_rr.get("status") != "approved":
            errors.append(
                f"Metoprolol refill status is '{metoprolol_rr.get('status')}', expected 'approved'."
            )
        if not metoprolol_rr.get("processedBy"):
            errors.append("Metoprolol refill processedBy is not set.")
        if not metoprolol_rr.get("processedDate"):
            errors.append("Metoprolol refill processedDate is not set.")

    if errors:
        return False, " | ".join(errors)

    return True, (
        f"All pending CVS refills processed correctly. "
        f"Lisinopril=approved, Atorvastatin=denied (reason='{atorvastatin_rr.get('denyReason', atorvastatin_rr.get('denialReason', ''))}'), "
        f"Gabapentin=approved, Omeprazole=approved, Metoprolol=approved."
    )
