import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Amlodipine was discontinued and a pharmacy cancel was sent."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    errors = []
    med_name_fragment = "amlodipine"
    dose_fragment = "5mg"

    # Check that Amlodipine 5mg is NOT in permanentRxMeds
    permanent_rx_meds = state.get("permanentRxMeds", [])
    amlodipine_active = [
        m for m in permanent_rx_meds
        if med_name_fragment in m.get("medicationName", "").lower()
        and dose_fragment in m.get("medicationName", "").lower()
    ]
    if amlodipine_active:
        errors.append("Amlodipine 5mg is still in permanentRxMeds; expected it to be discontinued")

    # Check that Amlodipine 5mg IS in discontinuedMeds
    discontinued_meds = state.get("discontinuedMeds", [])
    amlodipine_disc = [
        m for m in discontinued_meds
        if med_name_fragment in m.get("medicationName", "").lower()
        and dose_fragment in m.get("medicationName", "").lower()
    ]
    if not amlodipine_disc:
        errors.append("Amlodipine 5mg not found in discontinuedMeds")

    # Check canceledScripts has a new entry for Amlodipine (seed has 2, should be 3)
    canceled_scripts = state.get("canceledScripts", [])
    amlodipine_canceled = [
        c for c in canceled_scripts
        if med_name_fragment in c.get("medicationName", "").lower()
        and dose_fragment in c.get("medicationName", "").lower()
    ]
    if not amlodipine_canceled:
        errors.append(
            "No canceled script found for Amlodipine 5mg in canceledScripts; "
            "expected a cancel request to be sent to the pharmacy"
        )

    if len(canceled_scripts) < 3:
        errors.append(
            f"Expected at least 3 canceledScripts (seed had 2), found {len(canceled_scripts)}"
        )

    if errors:
        return False, f"Amlodipine discontinuation issues: {'; '.join(errors)}"

    return True, (
        "Amlodipine 5mg successfully discontinued and pharmacy cancel sent. "
        "Removed from permanentRxMeds, added to discontinuedMeds, "
        "and a new entry created in canceledScripts."
    )
