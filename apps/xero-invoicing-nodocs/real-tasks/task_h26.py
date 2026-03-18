import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Record full payments for all overdue AUD invoices using AUD Holding Account,
    and all overdue NZD invoices over $10,000 using Business Cheque Account."""
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

    # Build payment lookup by invoiceId
    payments_by_invoice = {}
    for p in payments:
        inv_id = p.get("invoiceId")
        if inv_id not in payments_by_invoice:
            payments_by_invoice[inv_id] = []
        payments_by_invoice[inv_id].append(p)

    # Check 1: No AUD invoice should remain overdue
    for inv in invoices:
        if inv.get("status") == "overdue" and inv.get("currency") == "AUD":
            errors.append(
                f"Invoice {inv.get('invoiceNumber')} is still overdue with currency AUD"
            )

    # Check 2: No NZD invoice with total > 10000 should remain overdue
    for inv in invoices:
        if (
            inv.get("status") == "overdue"
            and inv.get("currency") == "NZD"
            and inv.get("total", 0) > 10000
        ):
            errors.append(
                f"Invoice {inv.get('invoiceNumber')} is still overdue (NZD, total={inv.get('total')})"
            )

    # Check 3: Verify AUD invoices that are now paid have payment via bank_4 (AUD Holding Account)
    # Known seed AUD overdue: INV-0033 (inv_33), INV-0102 (inv_102)
    aud_overdue_ids = {"inv_33", "inv_102"}
    for inv_id in aud_overdue_ids:
        inv = None
        for i in invoices:
            if i.get("id") == inv_id:
                inv = i
                break
        if inv is None:
            continue
        if inv.get("status") == "paid":
            inv_payments = payments_by_invoice.get(inv_id, [])
            has_bank4 = any(p.get("bankAccountId") == "bank_4" for p in inv_payments)
            if not has_bank4:
                errors.append(
                    f"Invoice {inv.get('invoiceNumber')} (AUD) is paid but has no payment via "
                    f"bank_4 (AUD Holding Account)"
                )

    # Check 4: Verify NZD >10k invoices that are now paid have payment via bank_1 (Business Cheque Account)
    # Known seed NZD overdue >10k: INV-0015 (inv_15), INV-0040 (inv_40), INV-0059 (inv_59),
    #                               INV-0063 (inv_63), INV-0100 (inv_100)
    nzd_overdue_10k_ids = {"inv_15", "inv_40", "inv_59", "inv_63", "inv_100"}
    for inv_id in nzd_overdue_10k_ids:
        inv = None
        for i in invoices:
            if i.get("id") == inv_id:
                inv = i
                break
        if inv is None:
            continue
        if inv.get("status") == "paid":
            inv_payments = payments_by_invoice.get(inv_id, [])
            has_bank1 = any(p.get("bankAccountId") == "bank_1" for p in inv_payments)
            if not has_bank1:
                errors.append(
                    f"Invoice {inv.get('invoiceNumber')} (NZD >$10k) is paid but has no payment via "
                    f"bank_1 (Business Cheque Account)"
                )

    if errors:
        return False, "; ".join(errors)

    return True, (
        "All overdue AUD invoices paid via AUD Holding Account and all overdue NZD invoices "
        "over $10,000 paid via Business Cheque Account"
    )
