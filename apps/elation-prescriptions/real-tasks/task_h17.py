import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify Omeprazole was discontinued and Famotidine 20mg BID was prescribed to CVS."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    permanent_rx_meds = state.get("permanentRxMeds", [])
    discontinued_meds = state.get("discontinuedMeds", [])

    errors = []

    # --- Part A: Omeprazole should NOT be in permanentRxMeds ---
    omeprazole_in_rx = None
    for med in permanent_rx_meds:
        med_name = (med.get("medicationName") or "").lower()
        if "omeprazole" in med_name:
            omeprazole_in_rx = med
            break

    if omeprazole_in_rx is not None:
        errors.append(
            f"Omeprazole is still in permanentRxMeds ('{omeprazole_in_rx.get('medicationName')}'). "
            f"Expected it to be discontinued."
        )

    # Omeprazole should be in discontinuedMeds
    omeprazole_in_disc = None
    for med in discontinued_meds:
        med_name = (med.get("medicationName") or "").lower()
        if "omeprazole" in med_name:
            omeprazole_in_disc = med
            break

    if omeprazole_in_disc is None:
        disc_names = [m.get("medicationName", "") for m in discontinued_meds]
        errors.append(
            f"Omeprazole not found in discontinuedMeds. "
            f"Current discontinued meds: {disc_names}"
        )

    # --- Part B: Famotidine 20mg should be in permanentRxMeds ---
    famotidine_med = None
    for med in permanent_rx_meds:
        med_name = (med.get("medicationName") or "").lower()
        if "famotidine" in med_name and "20mg" in med_name:
            famotidine_med = med
            break

    if famotidine_med is None:
        med_names = [m.get("medicationName", "") for m in permanent_rx_meds]
        errors.append(
            f"No medication containing 'Famotidine' and '20mg' found in permanentRxMeds. "
            f"Current meds: {med_names}"
        )
    else:
        # Check qty = 60
        qty = famotidine_med.get("qty")
        if qty != 60:
            errors.append(f"Famotidine qty is {qty}, expected 60.")

        # Check refills = 3
        refills = famotidine_med.get("refills")
        if refills != 3:
            errors.append(f"Famotidine refills is {refills}, expected 3.")

        # Check pharmacy contains "CVS" (case-insensitive)
        pharmacy_name = (famotidine_med.get("pharmacyName") or "").lower()
        if "cvs" not in pharmacy_name:
            errors.append(
                f"Famotidine pharmacyName is '{famotidine_med.get('pharmacyName')}', "
                f"expected it to contain 'CVS'."
            )

        # Check sig mentions twice daily / BID
        sig = (famotidine_med.get("sig") or "").lower()
        bid_keywords = [
            "twice daily", "bid", "two times daily", "2 times daily",
            "twice a day", "every 12 hours", "q12h"
        ]
        has_bid = any(kw in sig for kw in bid_keywords)
        if not has_bid:
            errors.append(
                f"Famotidine sig does not indicate twice daily dosing. "
                f"sig='{famotidine_med.get('sig')}'."
            )

    if errors:
        return False, " | ".join(errors)

    return True, (
        f"Omeprazole discontinued and Famotidine 20mg prescribed successfully. "
        f"Famotidine: qty={famotidine_med.get('qty')}, refills={famotidine_med.get('refills')}, "
        f"pharmacy='{famotidine_med.get('pharmacyName')}', sig='{famotidine_med.get('sig')}'."
    )
