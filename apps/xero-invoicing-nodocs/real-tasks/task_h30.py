import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Change prefix to KPS-, then create draft invoice for Summit Financial Advisors."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    contacts = state.get("contacts", [])
    invoices = state.get("invoices", [])
    settings = state.get("settings", {})

    errors = []

    # Check invoice number prefix
    prefix = settings.get("invoiceNumberPrefix")
    if prefix != "KPS-":
        errors.append(f"settings.invoiceNumberPrefix is '{prefix}', expected 'KPS-'")

    # Find Summit Financial Advisors
    summit = None
    for c in contacts:
        if c.get("name") == "Summit Financial Advisors":
            summit = c
            break

    if summit is None:
        return False, "Contact 'Summit Financial Advisors' not found; " + "; ".join(errors) if errors else "Contact 'Summit Financial Advisors' not found"

    summit_id = summit.get("id")

    # Find a draft invoice for Summit Financial Advisors
    draft_inv = None
    for inv in invoices:
        if inv.get("contactId") == summit_id and inv.get("status") == "draft":
            draft_inv = inv
            break

    if draft_inv is None:
        errors.append("No draft invoice found for Summit Financial Advisors")
        return False, "; ".join(errors)

    # Check line items
    line_items = draft_inv.get("lineItems", [])
    found_retainer = False
    for li in line_items:
        desc = (li.get("description") or "").lower()
        if "advisory retainer" in desc:
            found_retainer = True
            if li.get("quantity") != 1:
                errors.append(
                    f"Advisory retainer line item quantity is {li.get('quantity')}, expected 1"
                )
            if li.get("unitPrice") != 12000:
                errors.append(
                    f"Advisory retainer line item unitPrice is {li.get('unitPrice')}, expected 12000"
                )
            break

    if not found_retainer:
        errors.append(
            "No line item with description containing 'advisory retainer' found in the draft invoice"
        )

    # Check dates
    if draft_inv.get("issueDate") != "2026-03-18":
        errors.append(
            f"Invoice issueDate is '{draft_inv.get('issueDate')}', expected '2026-03-18'"
        )

    if draft_inv.get("dueDate") != "2026-04-17":
        errors.append(
            f"Invoice dueDate is '{draft_inv.get('dueDate')}', expected '2026-04-17'"
        )

    if errors:
        return False, "; ".join(errors)

    return True, (
        f"Invoice prefix set to 'KPS-' and draft invoice {draft_inv.get('invoiceNumber')} "
        f"created for Summit Financial Advisors with advisory retainer line item"
    )
