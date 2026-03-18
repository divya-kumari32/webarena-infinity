import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Void overdue invoices due in 2025, pay overdue invoices due in 2026."""
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
    voided_count = 0
    paid_count = 0

    # No overdue invoices should remain
    still_overdue = [inv for inv in invoices if inv.get("status") == "overdue"]
    if still_overdue:
        for inv in still_overdue:
            errors.append(
                f"{inv.get('invoiceNumber')} (due {inv.get('dueDate')}) is still overdue"
            )
        return False, "; ".join(errors)

    # Check voided invoices with 2025 due dates
    for inv in invoices:
        due_date = inv.get("dueDate", "")
        if inv.get("status") == "voided" and due_date < "2026-01-01":
            voided_count += 1

    # Check paid invoices with 2026 due dates that have a bank_1 payment
    # matching the full invoice total (indicating they were paid by the solver)
    for inv in invoices:
        due_date = inv.get("dueDate", "")
        if inv.get("status") == "paid" and due_date >= "2026-01-01":
            inv_payments = [p for p in payments if p.get("invoiceId") == inv.get("id")]
            # Check if there's a full-amount payment via bank_1
            has_full_bank1 = any(
                p.get("bankAccountId") == "bank_1"
                and abs((p.get("amount", 0) or 0) - inv.get("total", 0)) < 0.01
                for p in inv_payments
            )
            if has_full_bank1:
                paid_count += 1

    if voided_count == 0:
        return False, "No 2025-due overdue invoices were voided"
    if paid_count == 0:
        return False, "No 2026-due overdue invoices were paid"

    return True, (
        f"2025-due overdue invoices voided ({voided_count}), "
        f"2026-due overdue invoices paid ({paid_count})"
    )
