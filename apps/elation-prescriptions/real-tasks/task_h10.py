import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the controlled substance (Alprazolam) was discontinued and cancel script created."""
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

    # Check Alprazolam is NOT in permanentRxMeds
    for med in permanent_rx_meds:
        if "Alprazolam" in med.get("medicationName", ""):
            errors.append(
                f"Alprazolam still found in permanentRxMeds: '{med.get('medicationName')}'"
            )
            break

    # Also verify no other controlled substances remain that shouldn't
    # (Alprazolam 0.5mg was the only controlled substance in seed data)
    remaining_controlled = [
        med for med in permanent_rx_meds
        if med.get("isControlled") is True
    ]
    # This is informational - the main check is Alprazolam specifically

    # Check Alprazolam IS in discontinuedMeds
    alprazolam_discontinued = None
    for med in discontinued_meds:
        if "Alprazolam" in med.get("medicationName", ""):
            alprazolam_discontinued = med
            break

    if alprazolam_discontinued is None:
        errors.append("Alprazolam not found in discontinuedMeds")

    # Check canceledScripts has new entry for Alprazolam (seed has 2, now should be 3+)
    alprazolam_cancels = [
        cs for cs in canceled_scripts
        if "Alprazolam" in cs.get("medicationName", "")
    ]

    if len(canceled_scripts) < 3:
        errors.append(
            f"canceledScripts has {len(canceled_scripts)} entries, expected at least 3 "
            f"(seed had 2, plus new Alprazolam cancel)"
        )

    if len(alprazolam_cancels) == 0:
        errors.append("No canceled script found for Alprazolam in canceledScripts")

    if errors:
        return False, "Failures: " + "; ".join(errors)

    return True, (
        "Controlled substance (Alprazolam 0.5mg) discontinued and pharmacy cancel created successfully. "
        f"Removed from permanentRxMeds, added to discontinuedMeds, "
        f"and pharmacy cancel script created ({len(canceled_scripts)} total canceled scripts)."
    )
