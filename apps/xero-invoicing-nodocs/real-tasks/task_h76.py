import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Update notes on PROJ- awaiting_payment invoices."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    invoices = state.get("invoices", [])
    errors = []
    updated_count = 0
    expected_notes = "Project invoice - quarterly review required"

    for inv in invoices:
        ref = inv.get("reference", "")
        status = inv.get("status")
        inv_num = inv.get("invoiceNumber")

        if ref.startswith("PROJ-") and status == "awaiting_payment":
            if inv.get("notes") != expected_notes:
                errors.append(
                    f"{inv_num} (PROJ-, awaiting_payment) notes is "
                    f"'{inv.get('notes')}', expected '{expected_notes}'"
                )
            else:
                updated_count += 1

    if errors:
        return False, "; ".join(errors)

    if updated_count == 0:
        return False, "No PROJ- awaiting_payment invoices had their notes updated"

    return True, f"Notes updated on {updated_count} PROJ- awaiting_payment invoice(s)"
