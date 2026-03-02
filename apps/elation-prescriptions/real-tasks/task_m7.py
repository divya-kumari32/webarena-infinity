import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Montelukast was discontinued because the patient stopped taking it."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    errors = []

    # Check that Montelukast is NOT in permanentRxMeds
    permanent_rx_meds = state.get("permanentRxMeds", [])
    montelukast_active = [
        m for m in permanent_rx_meds
        if "montelukast" in m.get("medicationName", "").lower()
    ]
    if montelukast_active:
        errors.append("Montelukast is still in permanentRxMeds; expected it to be discontinued")

    # Check that Montelukast IS in discontinuedMeds
    discontinued_meds = state.get("discontinuedMeds", [])
    montelukast_disc = [
        m for m in discontinued_meds
        if "montelukast" in m.get("medicationName", "").lower()
    ]
    if not montelukast_disc:
        errors.append("Montelukast not found in discontinuedMeds")
    else:
        med = montelukast_disc[0]

        # Check discontinueReason contains "patient stopped" (case insensitive)
        disc_reason = med.get("discontinueReason", "")
        if "patient stopped" not in disc_reason.lower():
            errors.append(
                f"Montelukast discontinueReason is '{disc_reason}', "
                "expected it to contain 'patient stopped' (case insensitive)"
            )

    if errors:
        return False, f"Montelukast discontinuation issues: {'; '.join(errors)}"

    return True, (
        "Montelukast successfully discontinued. "
        "Removed from permanentRxMeds, added to discontinuedMeds with "
        f"discontinueReason containing 'patient stopped'."
    )
