import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Half-payment on every overdue invoice."""
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
    paid_count = 0

    for inv in invoices:
        # After half-payment, invoice should still be overdue or awaiting_payment
        # (half never covers full amount unless total is 0)
        status = inv.get("status")
        if status not in ("overdue", "awaiting_payment"):
            continue

        inv_id = inv.get("id")
        inv_num = inv.get("invoiceNumber")
        total = inv.get("total", 0)

        # Check if this invoice had a half-payment recorded
        inv_payments = [p for p in payments if p.get("invoiceId") == inv_id]
        half_amount = round(total / 2, 2)

        has_half = any(
            abs((p.get("amount", 0) or 0) - half_amount) < 0.01
            and p.get("bankAccountId") == "bank_1"
            for p in inv_payments
        )

        # Only flag invoices that are still overdue without the half payment
        if status == "overdue" and not has_half:
            errors.append(
                f"{inv_num} (overdue, total={total}) has no half-payment "
                f"of ${half_amount:.2f}"
            )
        elif has_half:
            paid_count += 1

    if errors:
        return False, "; ".join(errors)

    if paid_count == 0:
        return False, "No overdue invoices received a half-payment"

    return True, f"Half-payment recorded on {paid_count} overdue invoice(s)"
