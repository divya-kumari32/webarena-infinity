import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the Metoprolol refill was approved with directions changed to once daily in the morning."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    errors = []

    # Find the Metoprolol refill request
    refill_requests = state.get("refillRequests", [])
    metoprolol_refill = None
    for rr in refill_requests:
        med_name = rr.get("medicationName", "")
        if "metoprolol" in med_name.lower():
            metoprolol_refill = rr
            break

    if metoprolol_refill is None:
        return False, "No refill request found for Metoprolol."

    # Check status is approved
    status = metoprolol_refill.get("status")
    if status != "approved":
        errors.append(f"Refill request status is '{status}', expected 'approved'")

    # Check processedBy is set
    processed_by = metoprolol_refill.get("processedBy")
    if not processed_by:
        errors.append("Refill request processedBy is not set")

    # Check modifications.sig contains "morning"
    modifications = metoprolol_refill.get("modifications", {})
    if not modifications:
        errors.append("Refill request has no modifications recorded")
    else:
        mod_sig = modifications.get("sig", "")
        if "morning" not in mod_sig.lower():
            errors.append(
                f"Refill modifications sig is '{mod_sig}', expected it to contain 'morning'"
            )

    # Find the Metoprolol medication in permanentRxMeds
    permanent_rx_meds = state.get("permanentRxMeds", [])
    metoprolol_med = None
    for med in permanent_rx_meds:
        med_name = med.get("medicationName", "")
        if "metoprolol" in med_name.lower():
            metoprolol_med = med
            break

    if metoprolol_med is None:
        errors.append("Metoprolol not found in permanentRxMeds")
    else:
        # Check sig updated to contain "morning"
        actual_sig = metoprolol_med.get("sig", "")
        if "morning" not in actual_sig.lower():
            errors.append(
                f"Metoprolol medication sig is '{actual_sig}', expected it to contain 'morning'"
            )

        # Check lastPrescribedDate updated from seed value "2025-11-20"
        last_prescribed = metoprolol_med.get("lastPrescribedDate")
        if last_prescribed == "2025-11-20":
            errors.append(
                "lastPrescribedDate is still the seed value '2025-11-20', expected it to be updated"
            )
        if not last_prescribed:
            errors.append("lastPrescribedDate is not set on Metoprolol in permanentRxMeds")

    if errors:
        return False, f"Metoprolol refill approval issues: {'; '.join(errors)}"

    return True, (
        f"Metoprolol refill approved with morning directions. "
        f"Refill status='approved', processedBy='{processed_by}', "
        f"sig updated to contain 'morning', lastPrescribedDate updated."
    )
