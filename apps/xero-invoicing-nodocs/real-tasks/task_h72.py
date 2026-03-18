import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Create Rotorua Geothermal Energy Ltd, create invoice with 3 line items,
    approve+send, record $5,000 partial payment."""
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

    # Find contact
    contact = next(
        (c for c in contacts if c.get("name") == "Rotorua Geothermal Energy Ltd"),
        None,
    )
    if contact is None:
        return False, "Contact 'Rotorua Geothermal Energy Ltd' not found"

    contact_id = contact.get("id")

    # Verify contact fields
    if contact.get("email") != "power@rotoruageo.co.nz":
        errors.append(f"email is '{contact.get('email')}', expected 'power@rotoruageo.co.nz'")
    if contact.get("phone") != "+64 7 348 9900":
        errors.append(f"phone is '{contact.get('phone')}', expected '+64 7 348 9900'")
    if contact.get("taxId") != "NZ-77-444-555":
        errors.append(f"taxId is '{contact.get('taxId')}', expected 'NZ-77-444-555'")

    addr = contact.get("billingAddress", {}) or {}
    expected_addr = {
        "street": "1167 Fenton Street",
        "city": "Rotorua",
        "region": "Bay of Plenty",
        "postalCode": "3010",
        "country": "New Zealand",
    }
    for field, val in expected_addr.items():
        actual = (addr.get(field) or "").strip()
        if actual != val:
            errors.append(f"billingAddress.{field} is '{actual}', expected '{val}'")

    # Find invoice for this contact
    inv = next(
        (i for i in invoices if i.get("contactId") == contact_id), None
    )
    if inv is None:
        errors.append("No invoice found for Rotorua Geothermal Energy Ltd")
        return False, "; ".join(errors)

    # Status should be awaiting_payment (approved, sent, partially paid)
    if inv.get("status") != "awaiting_payment":
        errors.append(f"Invoice status is '{inv.get('status')}', expected 'awaiting_payment'")

    # Should have sentAt
    if not inv.get("sentAt"):
        errors.append("Invoice has no sentAt timestamp")

    # Check line items
    line_items = inv.get("lineItems", [])
    if len(line_items) != 3:
        errors.append(f"Invoice has {len(line_items)} line items, expected 3")

    survey = next((li for li in line_items if "geothermal" in (li.get("description") or "").lower() and "survey" in (li.get("description") or "").lower()), None)
    if survey is None:
        errors.append("No line item containing 'geothermal survey'")
    else:
        if survey.get("quantity") != 5:
            errors.append(f"Geothermal survey qty is {survey.get('quantity')}, expected 5")
        if abs((survey.get("unitPrice") or 0) - 1500) > 0.01:
            errors.append(f"Geothermal survey unitPrice is {survey.get('unitPrice')}, expected 1500")

    drilling = next((li for li in line_items if "drilling" in (li.get("description") or "").lower()), None)
    if drilling is None:
        errors.append("No line item containing 'drilling'")
    else:
        if drilling.get("quantity") != 10:
            errors.append(f"Drilling qty is {drilling.get('quantity')}, expected 10")
        if abs((drilling.get("unitPrice") or 0) - 800) > 0.01:
            errors.append(f"Drilling unitPrice is {drilling.get('unitPrice')}, expected 800")

    safety = next((li for li in line_items if "safety" in (li.get("description") or "").lower()), None)
    if safety is None:
        errors.append("No line item containing 'safety'")
    else:
        if safety.get("quantity") != 1:
            errors.append(f"Safety qty is {safety.get('quantity')}, expected 1")
        if abs((safety.get("unitPrice") or 0) - 3000) > 0.01:
            errors.append(f"Safety unitPrice is {safety.get('unitPrice')}, expected 3000")

    # Check dates and reference
    if inv.get("issueDate") != "2026-03-18":
        errors.append(f"issueDate is '{inv.get('issueDate')}', expected '2026-03-18'")
    if inv.get("dueDate") != "2026-05-17":
        errors.append(f"dueDate is '{inv.get('dueDate')}', expected '2026-05-17'")
    if inv.get("reference") != "GEO-2026-001":
        errors.append(f"reference is '{inv.get('reference')}', expected 'GEO-2026-001'")

    # Check $5,000 partial payment
    inv_payments = [p for p in payments if p.get("invoiceId") == inv.get("id")]
    if not inv_payments:
        errors.append("No payment recorded on the invoice")
    else:
        total_paid = sum(p.get("amount", 0) for p in inv_payments)
        if abs(total_paid - 5000) > 0.01:
            errors.append(f"Total paid is ${total_paid}, expected $5,000")
        bank_ids = [p.get("bankAccountId") for p in inv_payments]
        if "bank_1" not in bank_ids:
            errors.append("No payment via bank_1 (Business Cheque Account)")

    if abs((inv.get("amountPaid") or 0) - 5000) > 0.01:
        errors.append(f"amountPaid is {inv.get('amountPaid')}, expected 5000")

    if errors:
        return False, "; ".join(errors)
    return True, "Rotorua Geothermal Energy Ltd created, invoice approved+sent, $5,000 partial payment recorded"
