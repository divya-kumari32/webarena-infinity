import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Mark as sent all awaiting_payment invoices for contacts with overdue invoices."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    invoices = state.get("invoices", [])
    errors = []

    # Find contacts with overdue invoices
    overdue_contact_ids = set()
    for inv in invoices:
        if inv.get("status") == "overdue":
            overdue_contact_ids.add(inv.get("contactId"))

    if not overdue_contact_ids:
        return False, "No contacts with overdue invoices found"

    sent_count = 0
    for inv in invoices:
        if (inv.get("status") == "awaiting_payment"
                and inv.get("contactId") in overdue_contact_ids):
            if not inv.get("sentAt"):
                errors.append(
                    f"{inv.get('invoiceNumber')} (awaiting_payment, contact has overdue) "
                    f"has no sentAt — should have been marked as sent"
                )
            else:
                sent_count += 1

    if errors:
        return False, "; ".join(errors)

    if sent_count == 0:
        return False, "No awaiting_payment invoices were marked as sent"

    return True, f"{sent_count} awaiting_payment invoice(s) marked as sent for contacts with overdue invoices"
