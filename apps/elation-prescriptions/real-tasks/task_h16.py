import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the Lisinopril 10mg template sig was updated to specify morning."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    rx_templates = state.get("rxTemplates", [])

    # Find the Lisinopril 10mg template by name (case-insensitive)
    lisinopril_template = None
    for tpl in rx_templates:
        med_name = (tpl.get("medicationName") or "").lower()
        if "lisinopril" in med_name and "10mg" in med_name:
            lisinopril_template = tpl
            break

    if lisinopril_template is None:
        tpl_names = [t.get("medicationName", "") for t in rx_templates]
        return False, (
            f"No template containing 'Lisinopril' and '10mg' found in rxTemplates. "
            f"Current templates: {tpl_names}"
        )

    # Check sig contains "morning" (case-insensitive)
    sig = (lisinopril_template.get("sig") or "").lower()
    if "morning" not in sig:
        return False, (
            f"Lisinopril 10mg template sig does not contain 'morning'. "
            f"sig='{lisinopril_template.get('sig')}'. "
            f"Seed sig was 'Take 1 tablet by mouth once daily'."
        )

    # Verify the sig changed from the seed value
    seed_sig = "Take 1 tablet by mouth once daily"
    if lisinopril_template.get("sig") == seed_sig:
        return False, (
            f"Lisinopril 10mg template sig is still the seed value '{seed_sig}'. "
            f"Expected it to be updated to mention 'morning'."
        )

    return True, (
        f"Lisinopril 10mg template sig updated successfully. "
        f"New sig='{lisinopril_template.get('sig')}'."
    )
