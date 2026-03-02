import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Sertraline was discontinued and a pharmacy cancel script was created."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    permanent_rx_meds = state.get("permanentRxMeds", [])
    discontinued_meds = state.get("discontinuedMeds", [])
    canceled_scripts = state.get("canceledScripts", [])
    errors = []

    # Check Sertraline is NOT in permanentRxMeds
    for med in permanent_rx_meds:
        if "Sertraline" in med.get("medicationName", ""):
            errors.append(
                f"Sertraline still found in permanentRxMeds: '{med.get('medicationName')}'"
            )
            break

    # Check Sertraline IS in discontinuedMeds with status="discontinued"
    sertraline_discontinued = None
    for med in discontinued_meds:
        if "Sertraline" in med.get("medicationName", ""):
            sertraline_discontinued = med
            break

    if sertraline_discontinued is None:
        errors.append("Sertraline not found in discontinuedMeds")
    else:
        if sertraline_discontinued.get("status") != "discontinued":
            errors.append(
                f"Sertraline in discontinuedMeds has status '{sertraline_discontinued.get('status')}', "
                f"expected 'discontinued'"
            )

    # Check canceledScripts has new entry for Sertraline (seed has 2, now should be 3+)
    sertraline_cancels = [
        cs for cs in canceled_scripts
        if "Sertraline" in cs.get("medicationName", "")
    ]

    if len(canceled_scripts) < 3:
        errors.append(
            f"canceledScripts has {len(canceled_scripts)} entries, expected at least 3 "
            f"(seed had 2, plus new Sertraline cancel)"
        )

    if len(sertraline_cancels) == 0:
        errors.append("No canceled script found for Sertraline in canceledScripts")

    if errors:
        return False, "Failures: " + "; ".join(errors)

    return True, (
        "Sertraline discontinued successfully. "
        f"Removed from permanentRxMeds, added to discontinuedMeds (status='discontinued'), "
        f"and pharmacy cancel script created ({len(canceled_scripts)} total canceled scripts)."
    )
