import requests


def verify(server_url: str) -> tuple[bool, str]:
    """$1,000 partial payment on every overdue invoice for Auckland region
    contacts."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    invoices = state.get("invoices", [])
    payments = state.get("payments", [])
    errors = []

    # The Auckland overdue invoices by invoice number
    auckland_overdue_nums = ["INV-0015", "INV-0033", "INV-0040", "INV-0087"]

    found_count = 0
    for inv_num in auckland_overdue_nums:
        inv = next(
            (i for i in invoices if i.get("invoiceNumber") == inv_num), None
        )
        if inv is None:
            errors.append(f"{inv_num} not found in invoices")
            continue
        found_count += 1

        inv_id = inv.get("id")
        inv_payments = [p for p in payments if p.get("invoiceId") == inv_id]

        # Check that at least one payment of $1,000 exists
        has_1000_payment = any(
            abs((p.get("amount", 0) or 0) - 1000) < 0.01
            for p in inv_payments
        )
        if not has_1000_payment:
            payment_amounts = [p.get("amount") for p in inv_payments]
            errors.append(
                f"{inv_num} has no $1,000 payment. Payment amounts: {payment_amounts}"
            )

        # Check payment was via bank_1 (Business Cheque Account)
        has_bank1_payment = any(
            abs((p.get("amount", 0) or 0) - 1000) < 0.01
            and p.get("bankAccountId") == "bank_1"
            for p in inv_payments
        )
        if not has_bank1_payment and has_1000_payment:
            bank_ids = [
                p.get("bankAccountId")
                for p in inv_payments
                if abs((p.get("amount", 0) or 0) - 1000) < 0.01
            ]
            errors.append(
                f"{inv_num} $1,000 payment not via bank_1. Bank IDs: {bank_ids}"
            )

    if found_count == 0:
        errors.append("No Auckland overdue invoices found at all")

    if errors:
        return False, "Verification failed: " + "; ".join(errors)
    return True, "$1,000 partial payment recorded on all Auckland overdue invoices via Business Cheque Account"
