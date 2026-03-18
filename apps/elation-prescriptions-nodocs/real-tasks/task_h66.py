import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Kaiser patient (William): ARB to 320mg, approve urgent refill, deny routine."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    errors = []

    if state.get("currentPatientId") != "pat_004":
        errors.append(f"Expected currentPatientId 'pat_004' (William Thornton), got '{state.get('currentPatientId')}'.")

    # rx_022 Valsartan dosage to 320mg
    rx_022 = next((r for r in state["prescriptions"] if r["id"] == "rx_022"), None)
    if not rx_022:
        errors.append("Prescription rx_022 (Valsartan) not found.")
    elif rx_022.get("dosage") != "320mg":
        errors.append(f"Expected rx_022 dosage '320mg', got '{rx_022.get('dosage')}'.")

    # rr_010 urgent Furosemide -> approved
    rr_010 = next((r for r in state["refillRequests"] if r["id"] == "rr_010"), None)
    if not rr_010:
        errors.append("Refill request rr_010 not found.")
    elif rr_010.get("status") != "approved":
        errors.append(f"Expected rr_010 status 'approved', got '{rr_010.get('status')}'.")

    # rr_007 routine Valsartan -> denied
    rr_007 = next((r for r in state["refillRequests"] if r["id"] == "rr_007"), None)
    if not rr_007:
        errors.append("Refill request rr_007 not found.")
    elif rr_007.get("status") != "denied":
        errors.append(f"Expected rr_007 status 'denied', got '{rr_007.get('status')}'.")

    if errors:
        return False, " ".join(errors)
    return True, "William: Valsartan to 320mg, urgent refill approved, routine denied."
