import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Void all overdue invoices belonging to contacts whose billing city is Auckland."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    contacts = state.get("contacts", [])
    invoices = state.get("invoices", [])

    # Find Auckland contact IDs
    auckland_ids = set()
    for c in contacts:
        addr = c.get("billingAddress", {})
        if addr.get("city") == "Auckland":
            auckland_ids.add(c.get("id"))

    if not auckland_ids:
        return False, "No Auckland contacts found in state"

    errors = []
    voided_count = 0

    for inv in invoices:
        if inv.get("contactId") not in auckland_ids:
            continue

        status = inv.get("status")
        if status == "overdue":
            errors.append(
                f"Invoice {inv.get('invoiceNumber')} for Auckland contact still has status 'overdue'"
            )
        elif status == "voided":
            voided_count += 1

    if errors:
        return False, "; ".join(errors)

    if voided_count == 0:
        return False, "No voided invoices found for Auckland contacts — expected at least one"

    return True, f"All overdue Auckland invoices have been voided ({voided_count} voided invoice(s) found)"
