import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Famotidine 20mg was prescribed BID to CVS, 60 tabs, 3 refills, dispense as written."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    permanent_rx_meds = state.get("permanentRxMeds", [])

    # Find Famotidine entry (case-insensitive, must also contain "20mg")
    famotidine_med = None
    for med in permanent_rx_meds:
        name = (med.get("medicationName") or "").lower()
        if "famotidine" in name and "20mg" in name:
            famotidine_med = med
            break

    if famotidine_med is None:
        med_names = [m.get("medicationName", "") for m in permanent_rx_meds]
        return False, (
            f"No medication containing 'Famotidine' and '20mg' found in permanentRxMeds. "
            f"Current meds: {med_names}"
        )

    # Check quantity = 60
    qty = famotidine_med.get("qty")
    if qty != 60:
        return False, f"Famotidine qty is {qty}, expected 60"

    # Check refills = 3
    refills = famotidine_med.get("refills")
    if refills != 3:
        return False, f"Famotidine refills is {refills}, expected 3"

    # Check dispenseAsWritten = True
    daw = famotidine_med.get("dispenseAsWritten")
    if daw is not True:
        return False, f"Famotidine dispenseAsWritten is {daw}, expected true"

    # Check pharmacy contains "CVS"
    pharmacy_name = famotidine_med.get("pharmacyName") or ""
    if "cvs" not in pharmacy_name.lower():
        return False, f"Famotidine pharmacyName is '{pharmacy_name}', expected it to contain 'CVS'"

    # Check sig mentions twice daily / BID / similar
    sig = (famotidine_med.get("sig") or "").lower()
    bid_keywords = ["twice daily", "bid", "two times daily", "2 times daily", "twice a day", "every 12 hours", "q12h"]
    has_bid = any(kw in sig for kw in bid_keywords)
    if not has_bid:
        return False, (
            f"Famotidine sig does not indicate twice daily dosing. "
            f"sig='{famotidine_med.get('sig')}'"
        )

    return True, (
        f"Famotidine 20mg prescribed successfully. "
        f"qty={qty}, refills={refills}, dispenseAsWritten={daw}, "
        f"pharmacy='{pharmacy_name}', sig='{famotidine_med.get('sig')}'"
    )
