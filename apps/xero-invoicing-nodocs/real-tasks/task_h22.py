import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Record a full payment via the Business Cheque Account for the single overdue invoice with the highest total amount."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    invoices = state.get("invoices", [])
    payments = state.get("payments", [])

    # The highest-total overdue invoice in seed data is INV-0040 (total $121,725)
    target_inv = None
    for inv in invoices:
        if inv.get("invoiceNumber") == "INV-0040":
            target_inv = inv
            break

    if target_inv is None:
        return False, "Invoice INV-0040 not found in state"

    errors = []

    # Check status is paid
    status = target_inv.get("status")
    if status != "paid":
        errors.append(f"INV-0040 has status '{status}', expected 'paid'")

    # Check amountDue is effectively zero
    amount_due = target_inv.get("amountDue", 0)
    if amount_due is None:
        amount_due = 0
    if amount_due > 0.01:
        errors.append(f"INV-0040 has amountDue={amount_due}, expected <= 0.01")

    # Check that a payment exists for this invoice with bankAccountId 'bank_1' (Business Cheque Account)
    inv_id = target_inv.get("id")
    has_bank1_payment = False
    for p in payments:
        if p.get("invoiceId") == inv_id and p.get("bankAccountId") == "bank_1":
            has_bank1_payment = True
            break

    if not has_bank1_payment:
        errors.append(
            f"No payment found for INV-0040 (id={inv_id}) with bankAccountId 'bank_1' (Business Cheque Account)"
        )

    if errors:
        return False, "; ".join(errors)

    return True, "INV-0040 (highest overdue total $121,725) is fully paid via Business Cheque Account"
