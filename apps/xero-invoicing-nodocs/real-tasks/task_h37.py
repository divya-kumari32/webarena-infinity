import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Update the notes on every partially-paid invoice to
    'Partial payment received - follow up required'."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    invoices = state.get("invoices", [])
    errors = []
    expected_note = "Partial payment received - follow up required"

    # Known partially-paid invoices (amountPaid > 0 and still awaiting_payment/overdue with amountDue > 0)
    known_partial = ["INV-0006", "INV-0034", "INV-0055", "INV-0074"]

    # Check all invoices that are partially paid
    partial_invoices = [
        inv for inv in invoices
        if (inv.get("amountPaid", 0) or 0) > 0
        and inv.get("status") in ("awaiting_payment", "overdue")
        and (inv.get("amountDue", 0) or 0) > 0.01
    ]

    if not partial_invoices and not any(
        next((i for i in invoices if i.get("invoiceNumber") == num), None)
        for num in known_partial
    ):
        errors.append("No partially-paid invoices found at all")

    # Check the known partial invoices
    for inv_num in known_partial:
        inv = next(
            (i for i in invoices if i.get("invoiceNumber") == inv_num), None
        )
        if inv is None:
            errors.append(f"{inv_num} not found in invoices")
            continue
        notes = (inv.get("notes") or "").strip()
        if notes != expected_note:
            errors.append(
                f"{inv_num} notes is '{notes}', expected '{expected_note}'"
            )

    # Also check any other partially-paid invoices
    for inv in partial_invoices:
        inv_num = inv.get("invoiceNumber", "unknown")
        if inv_num in known_partial:
            continue  # Already checked above
        notes = (inv.get("notes") or "").strip()
        if notes != expected_note:
            errors.append(
                f"{inv_num} (partially paid) notes is '{notes}', expected '{expected_note}'"
            )

    if errors:
        return False, "Verification failed: " + "; ".join(errors)
    return True, "All partially-paid invoices have updated notes"
