import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Approve and send all draft invoices with a total exceeding $10,000."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    invoices = state.get("invoices", [])
    errors = []

    # Check no draft invoices with total > 10000 remain
    big_drafts = [
        inv for inv in invoices
        if inv.get("status") == "draft"
        and (inv.get("total", 0) or 0) > 10000
    ]
    if big_drafts:
        nums = [
            f"{inv.get('invoiceNumber')} (${inv.get('total')})"
            for inv in big_drafts
        ]
        errors.append(f"Draft invoices with total > $10,000 still exist: {nums}")

    # Verify each specific invoice is now awaiting_payment and was sent
    expected_invoices = ["INV-0025", "INV-0042", "INV-0061", "INV-0082", "INV-0093"]
    for inv_num in expected_invoices:
        inv = next(
            (i for i in invoices if i.get("invoiceNumber") == inv_num), None
        )
        if inv is None:
            errors.append(f"{inv_num} not found in invoices")
            continue
        if inv.get("status") != "awaiting_payment":
            errors.append(
                f"{inv_num} status is '{inv.get('status')}', expected 'awaiting_payment'"
            )
        sent_at = inv.get("sentAt")
        if not sent_at:
            errors.append(f"{inv_num} sentAt is empty or missing")

    if errors:
        return False, "Verification failed: " + "; ".join(errors)
    return True, "All draft invoices over $10,000 approved and sent"
