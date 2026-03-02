import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the Prednisone taper template was removed from rxTemplates."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    # Check rxTemplates for Prednisone taper
    rx_templates = state.get("rxTemplates", [])

    for template in rx_templates:
        med_name = template.get("medicationName", "")
        if "Prednisone" in med_name and "taper" in med_name.lower():
            return False, (
                f"Prednisone taper template still exists in rxTemplates: "
                f"medicationName='{med_name}'"
            )

    # Verify we didn't lose too many templates (seed had 12, should now have 11)
    if len(rx_templates) < 11:
        return False, (
            f"Expected at least 11 remaining templates after removing Prednisone taper, "
            f"but found {len(rx_templates)}. Other templates may have been accidentally removed."
        )

    return True, (
        f"Prednisone taper template removed successfully. "
        f"{len(rx_templates)} templates remain in rxTemplates."
    )
