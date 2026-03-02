import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the Metformin 500mg tablet template was updated to qty=90."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    rx_templates = state.get("rxTemplates", [])

    # Find the Metformin 500mg tablet template by name
    metformin_template = None
    for tpl in rx_templates:
        if tpl.get("medicationName") == "Metformin 500mg tablet":
            metformin_template = tpl
            break

    if metformin_template is None:
        # Try case-insensitive fallback
        for tpl in rx_templates:
            name = (tpl.get("medicationName") or "").lower()
            if "metformin" in name and "500mg" in name:
                metformin_template = tpl
                break

    if metformin_template is None:
        tpl_names = [t.get("medicationName", "") for t in rx_templates]
        return False, (
            f"No template with medicationName 'Metformin 500mg tablet' found. "
            f"Current templates: {tpl_names}"
        )

    # Check qty updated from 60 to 90
    qty = metformin_template.get("qty")
    if qty == 60:
        return False, "Metformin 500mg tablet template qty is still the seed value 60, expected 90"
    if qty != 90:
        return False, f"Metformin 500mg tablet template qty is {qty}, expected 90"

    return True, (
        f"Metformin 500mg tablet template updated successfully. "
        f"qty={qty} (was 60), medicationName='{metformin_template.get('medicationName')}'"
    )
