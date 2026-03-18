import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Three-region conditional on overdue invoices: void Otago, pay Waikato,
    $500 partial for Bay of Plenty."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    contacts = state.get("contacts", [])
    invoices = state.get("invoices", [])
    payments = state.get("payments", [])
    errors = []

    # Build region lookup
    contact_region = {}
    for c in contacts:
        addr = c.get("billingAddress", {})
        contact_region[c.get("id")] = addr.get("region", "")

    otago_voided = 0
    waikato_paid = 0
    bop_partial = 0
    total_processed = 0

    for inv in invoices:
        region = contact_region.get(inv.get("contactId"), "")
        inv_num = inv.get("invoiceNumber")
        status = inv.get("status")

        if region == "Otago":
            if status == "overdue":
                errors.append(
                    f"{inv_num} (Otago) still overdue, expected voided"
                )
            elif status == "voided":
                otago_voided += 1

        elif region == "Waikato":
            if status == "overdue":
                errors.append(
                    f"{inv_num} (Waikato) still overdue, expected paid"
                )
            elif status == "paid":
                inv_payments = [p for p in payments if p.get("invoiceId") == inv.get("id")]
                has_full_bank1 = any(
                    p.get("bankAccountId") == "bank_1"
                    and abs((p.get("amount", 0) or 0) - inv.get("total", 0)) < 0.01
                    for p in inv_payments
                )
                if has_full_bank1:
                    waikato_paid += 1

        elif region == "Bay of Plenty":
            if status in ("overdue", "awaiting_payment"):
                inv_payments = [
                    p for p in payments if p.get("invoiceId") == inv.get("id")
                ]
                has_500 = any(
                    abs((p.get("amount", 0) or 0) - 500) < 0.01
                    and p.get("bankAccountId") == "bank_1"
                    for p in inv_payments
                )
                if status == "overdue" and not has_500:
                    errors.append(
                        f"{inv_num} (Bay of Plenty) has no $500 partial payment"
                    )
                elif has_500:
                    bop_partial += 1

    total_processed = otago_voided + waikato_paid + bop_partial

    if errors:
        return False, "; ".join(errors)

    if total_processed == 0:
        return False, "No overdue invoices in Otago, Waikato, or Bay of Plenty were processed"

    parts = []
    if otago_voided > 0:
        parts.append(f"Otago voided ({otago_voided})")
    if waikato_paid > 0:
        parts.append(f"Waikato paid ({waikato_paid})")
    if bop_partial > 0:
        parts.append(f"Bay of Plenty $500 partial ({bop_partial})")

    return True, ", ".join(parts)
