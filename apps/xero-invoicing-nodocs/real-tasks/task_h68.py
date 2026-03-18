import requests


def verify(server_url: str) -> tuple[bool, str]:
    """$1,000 partial payment and notes update on QUO- overdue invoices."""
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
    matched_count = 0

    for inv in invoices:
        ref = inv.get("reference", "")
        if not ref.startswith("QUO-"):
            continue

        # This invoice had a QUO- reference. Check if it was originally overdue.
        # After partial payment it should still be overdue (or awaiting_payment if
        # the $1k covered the full amount, which is unlikely for these invoices).
        inv_id = inv.get("id")
        inv_num = inv.get("invoiceNumber")
        status = inv.get("status")

        # Must not still be fully overdue without payment
        inv_payments = [p for p in payments if p.get("invoiceId") == inv_id]

        # Check for $1,000 payment
        has_1000 = any(
            abs((p.get("amount", 0) or 0) - 1000) < 0.01
            for p in inv_payments
        )

        # Only check invoices that were overdue (status overdue or changed due to payment)
        if status in ("overdue", "awaiting_payment", "paid"):
            if not has_1000 and status == "overdue":
                errors.append(f"{inv_num} (QUO- overdue) has no $1,000 payment")
                continue

            if has_1000:
                matched_count += 1

                # Check payment via bank_1
                has_bank1_1000 = any(
                    abs((p.get("amount", 0) or 0) - 1000) < 0.01
                    and p.get("bankAccountId") == "bank_1"
                    for p in inv_payments
                )
                if not has_bank1_1000:
                    errors.append(f"{inv_num} $1,000 payment not via bank_1")

                # Check notes
                expected_notes = "Quote accepted - installment plan active"
                if inv.get("notes") != expected_notes:
                    errors.append(
                        f"{inv_num} notes is '{inv.get('notes')}', "
                        f"expected '{expected_notes}'"
                    )

    if errors:
        return False, "; ".join(errors)

    if matched_count == 0:
        return False, "No QUO- overdue invoices found with $1,000 payment"

    return True, f"$1,000 partial payment and notes updated on {matched_count} QUO- overdue invoice(s)"
