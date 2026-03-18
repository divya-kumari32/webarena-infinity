import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Create contact Alpine Ventures Ltd + create invoice with 2 line items + approve and send."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    contacts = state.get("contacts", [])
    invoices = state.get("invoices", [])

    errors = []

    # Find contact Alpine Ventures Ltd
    alpine = None
    for c in contacts:
        if c.get("name") == "Alpine Ventures Ltd":
            alpine = c
            break

    if alpine is None:
        return False, "Contact 'Alpine Ventures Ltd' not found"

    # Validate contact details
    if alpine.get("email") != "finance@alpineventures.co.nz":
        errors.append(f"Contact email is '{alpine.get('email')}', expected 'finance@alpineventures.co.nz'")

    if alpine.get("phone") != "+64 3 450 8800":
        errors.append(f"Contact phone is '{alpine.get('phone')}', expected '+64 3 450 8800'")

    addr = alpine.get("billingAddress", {})
    expected_addr = {
        "street": "42 Beach Street",
        "city": "Queenstown",
        "region": "Otago",
        "postalCode": "9300",
        "country": "New Zealand",
    }
    for field, expected in expected_addr.items():
        actual = addr.get(field)
        if actual != expected:
            errors.append(f"Contact billingAddress.{field} is '{actual}', expected '{expected}'")

    # Find invoice for Alpine Ventures
    alpine_id = alpine.get("id")
    alpine_invoices = [inv for inv in invoices if inv.get("contactId") == alpine_id]

    if not alpine_invoices:
        errors.append("No invoice found for Alpine Ventures Ltd")
        return False, "; ".join(errors)

    # Find the target invoice (should be awaiting_payment and sent)
    target_inv = None
    for inv in alpine_invoices:
        if inv.get("status") == "awaiting_payment" and inv.get("sentAt"):
            target_inv = inv
            break

    if target_inv is None:
        # Fallback: check any invoice for this contact
        target_inv = alpine_invoices[0]
        if target_inv.get("status") != "awaiting_payment":
            errors.append(
                f"Invoice {target_inv.get('invoiceNumber')} has status '{target_inv.get('status')}', "
                f"expected 'awaiting_payment'"
            )
        if not target_inv.get("sentAt"):
            errors.append(
                f"Invoice {target_inv.get('invoiceNumber')} has sentAt=None, expected it to be sent"
            )

    inv = target_inv

    # Check dates
    if inv.get("issueDate") != "2026-03-18":
        errors.append(f"Invoice issueDate is '{inv.get('issueDate')}', expected '2026-03-18'")

    if inv.get("dueDate") != "2026-04-17":
        errors.append(f"Invoice dueDate is '{inv.get('dueDate')}', expected '2026-04-17'")

    if inv.get("reference") != "AV-2026-001":
        errors.append(f"Invoice reference is '{inv.get('reference')}', expected 'AV-2026-001'")

    # Check line items
    line_items = inv.get("lineItems", [])
    if len(line_items) != 2:
        errors.append(f"Invoice has {len(line_items)} line item(s), expected 2")
    else:
        found_consulting = False
        found_research = False
        for li in line_items:
            desc = (li.get("description") or "").lower()
            if "strategic consulting" in desc:
                found_consulting = True
                if li.get("quantity") != 20:
                    errors.append(
                        f"Strategic consulting line item quantity is {li.get('quantity')}, expected 20"
                    )
                if li.get("unitPrice") != 250:
                    errors.append(
                        f"Strategic consulting line item unitPrice is {li.get('unitPrice')}, expected 250"
                    )
            elif "market research" in desc:
                found_research = True
                if li.get("quantity") != 1:
                    errors.append(
                        f"Market research line item quantity is {li.get('quantity')}, expected 1"
                    )
                if li.get("unitPrice") != 3500:
                    errors.append(
                        f"Market research line item unitPrice is {li.get('unitPrice')}, expected 3500"
                    )

        if not found_consulting:
            errors.append("No line item with description containing 'strategic consulting' found")
        if not found_research:
            errors.append("No line item with description containing 'market research' found")

    if errors:
        return False, "; ".join(errors)

    return True, (
        f"Alpine Ventures Ltd contact created correctly; invoice {inv.get('invoiceNumber')} "
        f"approved, sent, with correct line items, dates, and reference"
    )
