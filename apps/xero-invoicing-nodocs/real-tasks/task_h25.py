import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Send all invoices that are currently awaiting approval for contacts based in Auckland."""
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
    sent_count = 0

    for inv in invoices:
        if inv.get("contactId") not in auckland_ids:
            continue

        status = inv.get("status")
        if status == "awaiting_approval":
            errors.append(
                f"Invoice {inv.get('invoiceNumber')} for Auckland contact still has status 'awaiting_approval'"
            )

        # Count Auckland invoices that have been sent
        if inv.get("sentAt"):
            sent_count += 1

    if errors:
        return False, "; ".join(errors)

    if sent_count == 0:
        return False, "No Auckland contact invoices have sentAt set — expected at least one to be sent"

    return True, (
        f"All Auckland awaiting-approval invoices have been sent "
        f"({sent_count} Auckland invoice(s) with sentAt set)"
    )
