import requests


def verify(server_url: str) -> tuple[bool, str]:
    """$5,000 partial payment on each of the 3 overdue invoices with highest outstanding amounts."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    invoices = state.get("invoices", [])
    payments = state.get("payments", [])

    # The top 3 overdue invoices by total in seed data:
    # INV-0040 ($121,725) - inv_40
    # INV-0059 ($80,707) - inv_59
    # INV-0102 ($60,975.88) - inv_102
    target_invoices = {
        "INV-0040": "inv_40",
        "INV-0059": "inv_59",
        "INV-0102": "inv_102",
    }

    # Build payment lookup by invoiceId
    payments_by_invoice = {}
    for p in payments:
        inv_id = p.get("invoiceId")
        if inv_id not in payments_by_invoice:
            payments_by_invoice[inv_id] = []
        payments_by_invoice[inv_id].append(p)

    errors = []

    for inv_num, inv_id in target_invoices.items():
        # Find the invoice
        inv = None
        for i in invoices:
            if i.get("id") == inv_id:
                inv = i
                break

        if inv is None:
            errors.append(f"Invoice {inv_num} ({inv_id}) not found in state")
            continue

        # These should still be overdue (partial payment, not fully paid)
        status = inv.get("status")
        if status == "paid":
            errors.append(
                f"Invoice {inv_num} has status 'paid' — expected it to still be overdue "
                f"(only a $5,000 partial payment should have been made)"
            )

        # Check for a $5,000 payment
        inv_payments = payments_by_invoice.get(inv_id, [])
        has_5k_payment = False
        for p in inv_payments:
            amount = p.get("amount", 0)
            if isinstance(amount, (int, float)) and abs(amount - 5000) < 0.01:
                has_5k_payment = True
                break

        if not has_5k_payment:
            payment_amounts = [p.get("amount") for p in inv_payments]
            errors.append(
                f"Invoice {inv_num} has no $5,000 payment (found payments: {payment_amounts})"
            )

    if errors:
        return False, "; ".join(errors)

    return True, (
        "All 3 highest-outstanding overdue invoices (INV-0040, INV-0059, INV-0102) "
        "have received a $5,000 partial payment"
    )
