import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Delete all draft invoices that have no reference."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    invoices = state.get("invoices", [])
    errors = []

    # Check no draft invoices with empty reference remain
    drafts_no_ref = [
        inv for inv in invoices
        if inv.get("status") == "draft"
        and (not inv.get("reference") or str(inv.get("reference", "")).strip() == "")
    ]
    if drafts_no_ref:
        nums = [inv.get("invoiceNumber") for inv in drafts_no_ref]
        errors.append(f"Draft invoices with no reference still exist: {nums}")

    # Verify the specific invoices are gone entirely
    deleted_invoices = ["INV-0018", "INV-0020", "INV-0025", "INV-0093"]
    for inv_num in deleted_invoices:
        inv = next(
            (i for i in invoices if i.get("invoiceNumber") == inv_num), None
        )
        if inv is not None:
            errors.append(
                f"{inv_num} still exists in invoices (status: '{inv.get('status')}')"
            )

    if errors:
        return False, "Verification failed: " + "; ".join(errors)
    return True, "All draft invoices with no reference have been deleted"
