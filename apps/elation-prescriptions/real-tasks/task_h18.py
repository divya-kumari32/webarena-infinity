import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify Gabapentin refill approved with dose reduced to twice daily AND Gabapentin change request denied."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    errors = []

    # --- Part A: Gabapentin refill (rr_003) approved with twice daily modification ---
    refill_requests = state.get("refillRequests", [])

    # Find Gabapentin refill by medication name (case-insensitive)
    gabapentin_refill = None
    for rr in refill_requests:
        med_name = (rr.get("medicationName") or "").lower()
        notes = (rr.get("notes") or "").lower()
        if "gabapentin" in med_name and ("running low" in notes or rr.get("type") == "refill"):
            gabapentin_refill = rr
            break

    # Fallback: any Gabapentin refill request
    if gabapentin_refill is None:
        for rr in refill_requests:
            med_name = (rr.get("medicationName") or "").lower()
            if "gabapentin" in med_name and rr.get("type") == "refill":
                gabapentin_refill = rr
                break

    if gabapentin_refill is None:
        errors.append("Could not find a Gabapentin refill request in refillRequests.")
    else:
        # Check status approved
        refill_status = gabapentin_refill.get("status")
        if refill_status != "approved":
            errors.append(
                f"Gabapentin refill status is '{refill_status}', expected 'approved'."
            )

        # Check modifications.sig contains "twice daily" (case-insensitive)
        modifications = gabapentin_refill.get("modifications", {}) or {}
        mod_sig = (modifications.get("sig") or "").lower()
        bid_keywords = [
            "twice daily", "bid", "two times daily", "2 times daily",
            "twice a day", "every 12 hours", "q12h"
        ]
        has_mod_bid = any(kw in mod_sig for kw in bid_keywords)
        if not has_mod_bid:
            errors.append(
                f"Gabapentin refill modifications.sig does not contain 'twice daily'. "
                f"modifications.sig='{modifications.get('sig')}'. "
                f"Expected the dose to be reduced from three times daily to twice daily."
            )

    # Check Gabapentin med sig updated to twice daily
    permanent_rx_meds = state.get("permanentRxMeds", [])
    gabapentin_med = None
    for med in permanent_rx_meds:
        med_name = (med.get("medicationName") or "").lower()
        if "gabapentin" in med_name:
            gabapentin_med = med
            break

    if gabapentin_med is None:
        errors.append("Could not find Gabapentin in permanentRxMeds.")
    else:
        med_sig = (gabapentin_med.get("sig") or "").lower()
        has_bid = any(kw in med_sig for kw in bid_keywords)
        if not has_bid:
            errors.append(
                f"Gabapentin med sig does not contain 'twice daily'. "
                f"sig='{gabapentin_med.get('sig')}'. "
                f"Expected sig to be updated to twice daily."
            )

        # Check lastPrescribedDate updated from seed value
        last_prescribed = gabapentin_med.get("lastPrescribedDate")
        if last_prescribed == "2025-09-15":
            errors.append(
                f"Gabapentin lastPrescribedDate is still the seed value '2025-09-15'. "
                f"Expected it to be updated after refill approval."
            )

    # --- Part B: Gabapentin change request (sig clarification) denied ---
    change_requests = state.get("changeRequests", [])

    gabapentin_cr = None
    for cr in change_requests:
        original = (cr.get("originalMedication") or "").lower()
        requested = (cr.get("requestedMedication") or "").lower()
        # Sig clarification: original == requested and contains "gabapentin"
        if "gabapentin" in original and original == requested:
            gabapentin_cr = cr
            break

    # Fallback: any Gabapentin change request
    if gabapentin_cr is None:
        for cr in change_requests:
            med_name = (cr.get("medicationName") or "").lower()
            if "gabapentin" in med_name:
                gabapentin_cr = cr
                break

    if gabapentin_cr is None:
        errors.append("Could not find a Gabapentin change request (sig clarification).")
    else:
        cr_status = gabapentin_cr.get("status")
        if cr_status != "denied":
            errors.append(
                f"Gabapentin change request (sig clarification) status is '{cr_status}', "
                f"expected 'denied'."
            )

        processed_by = gabapentin_cr.get("processedBy")
        if not processed_by:
            errors.append("Gabapentin change request processedBy is not set.")

    if errors:
        return False, " | ".join(errors)

    return True, (
        f"Gabapentin refill approved with twice daily modification and change request denied. "
        f"Refill modifications.sig='{(gabapentin_refill.get('modifications') or {}).get('sig')}', "
        f"med sig='{gabapentin_med.get('sig')}', "
        f"lastPrescribedDate='{gabapentin_med.get('lastPrescribedDate')}', "
        f"change request status='denied'."
    )
