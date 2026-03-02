import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the Gabapentin refill was approved with dosing reduced to twice daily."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    errors = []

    # Find the Gabapentin refill request
    refill_requests = state.get("refillRequests", [])
    gabapentin_refill = None
    for rr in refill_requests:
        med_name = rr.get("medicationName", "")
        if "gabapentin" in med_name.lower() and "300mg" in med_name.lower():
            gabapentin_refill = rr
            break

    if gabapentin_refill is None:
        return False, "No refill request found for Gabapentin 300mg."

    # Check status is approved
    status = gabapentin_refill.get("status")
    if status != "approved":
        errors.append(f"Refill request status is '{status}', expected 'approved'")

    # Check processedBy is set
    processed_by = gabapentin_refill.get("processedBy")
    if not processed_by:
        errors.append("Refill request processedBy is not set")

    # Check processedDate is set
    processed_date = gabapentin_refill.get("processedDate")
    if not processed_date:
        errors.append("Refill request processedDate is not set")

    # Check modifications.sig contains "twice daily"
    modifications = gabapentin_refill.get("modifications", {})
    if not modifications:
        errors.append("Refill request has no modifications recorded")
    else:
        mod_sig = modifications.get("sig", "")
        if "twice daily" not in mod_sig.lower():
            errors.append(
                f"Refill modifications sig is '{mod_sig}', expected it to contain 'twice daily'"
            )

    # Find the Gabapentin medication in permanentRxMeds
    permanent_rx_meds = state.get("permanentRxMeds", [])
    gabapentin_med = None
    for med in permanent_rx_meds:
        med_name = med.get("medicationName", "")
        if "gabapentin" in med_name.lower() and "300mg" in med_name.lower():
            gabapentin_med = med
            break

    if gabapentin_med is None:
        errors.append("Gabapentin 300mg not found in permanentRxMeds")
    else:
        # Check sig updated to contain "twice daily"
        actual_sig = gabapentin_med.get("sig", "")
        if "twice daily" not in actual_sig.lower():
            errors.append(
                f"Gabapentin medication sig is '{actual_sig}', expected it to contain 'twice daily'"
            )

        # Check lastPrescribedDate updated from seed value "2025-09-15"
        last_prescribed = gabapentin_med.get("lastPrescribedDate")
        if last_prescribed == "2025-09-15":
            errors.append(
                "lastPrescribedDate is still the seed value '2025-09-15', expected it to be updated"
            )
        if not last_prescribed:
            errors.append("lastPrescribedDate is not set on Gabapentin in permanentRxMeds")

    if errors:
        return False, f"Gabapentin refill approval issues: {'; '.join(errors)}"

    return True, (
        f"Gabapentin 300mg refill approved with twice daily dosing. "
        f"Refill status='approved', processedBy='{processed_by}', "
        f"sig updated to contain 'twice daily', lastPrescribedDate updated."
    )
