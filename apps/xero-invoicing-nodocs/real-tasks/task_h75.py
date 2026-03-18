import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Pay Wellington overdue, void Bay of Plenty overdue."""
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

    wellington_paid = 0
    bop_voided = 0

    for inv in invoices:
        region = contact_region.get(inv.get("contactId"), "")
        inv_num = inv.get("invoiceNumber")
        status = inv.get("status")

        if region == "Wellington":
            if status == "overdue":
                errors.append(
                    f"{inv_num} (Wellington) still overdue, expected paid"
                )
            elif status == "paid":
                # Verify payment via bank_1
                inv_payments = [p for p in payments if p.get("invoiceId") == inv.get("id")]
                has_bank1 = any(p.get("bankAccountId") == "bank_1" for p in inv_payments)
                if not has_bank1:
                    errors.append(f"{inv_num} (Wellington) paid but not via bank_1")
                wellington_paid += 1

        elif region == "Bay of Plenty":
            if status == "overdue":
                errors.append(
                    f"{inv_num} (Bay of Plenty) still overdue, expected voided"
                )
            elif status == "voided":
                bop_voided += 1

    if errors:
        return False, "; ".join(errors)

    if wellington_paid == 0:
        return False, "No Wellington overdue invoices were paid"
    if bop_voided == 0:
        return False, "No Bay of Plenty overdue invoices were voided"

    return True, (
        f"Wellington overdue paid ({wellington_paid}), "
        f"Bay of Plenty overdue voided ({bop_voided})"
    )
