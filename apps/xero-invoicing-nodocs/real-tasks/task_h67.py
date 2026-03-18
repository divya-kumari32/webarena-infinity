import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Change prefix to FINAL-, padding to 6, then create draft for Atlas Import/Export."""
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

    # Check settings
    if settings.get("invoiceNumberPrefix") != "FINAL-":
        errors.append(
            f"Prefix is '{settings.get('invoiceNumberPrefix')}', expected 'FINAL-'"
        )
    if settings.get("invoiceNumberPadding") != 6:
        errors.append(
            f"Padding is {settings.get('invoiceNumberPadding')}, expected 6"
        )

    # Find Atlas Import/Export Ltd
    atlas = next(
        (c for c in contacts if c.get("name") == "Atlas Import/Export Ltd"), None
    )
    if atlas is None:
        return False, "Contact 'Atlas Import/Export Ltd' not found; " + "; ".join(errors) if errors else "Contact not found"

    atlas_id = atlas.get("id")

    # Find draft invoice for Atlas
    draft_inv = next(
        (inv for inv in invoices
         if inv.get("contactId") == atlas_id and inv.get("status") == "draft"
         and inv.get("reference") == "AIE-FINAL-001"),
        None,
    )
    if draft_inv is None:
        errors.append("No draft invoice with reference 'AIE-FINAL-001' found for Atlas Import/Export Ltd")
        return False, "; ".join(errors)

    # Check line items
    line_items = draft_inv.get("lineItems", [])
    if len(line_items) != 2:
        errors.append(f"Invoice has {len(line_items)} line items, expected 2")

    customs = next(
        (li for li in line_items
         if "customs" in (li.get("description") or "").lower()
         and "clearance" in (li.get("description") or "").lower()),
        None,
    )
    if customs is None:
        errors.append("No line item containing 'customs clearance'")
    else:
        if customs.get("quantity") != 1:
            errors.append(f"Customs clearance qty is {customs.get('quantity')}, expected 1")
        if abs((customs.get("unitPrice") or 0) - 1200) > 0.01:
            errors.append(f"Customs clearance unitPrice is {customs.get('unitPrice')}, expected 1200")

    freight = next(
        (li for li in line_items
         if "freight" in (li.get("description") or "").lower()),
        None,
    )
    if freight is None:
        errors.append("No line item containing 'freight'")
    else:
        if freight.get("quantity") != 3:
            errors.append(f"Freight qty is {freight.get('quantity')}, expected 3")
        if abs((freight.get("unitPrice") or 0) - 850) > 0.01:
            errors.append(f"Freight unitPrice is {freight.get('unitPrice')}, expected 850")

    # Check dates
    if draft_inv.get("issueDate") != "2026-03-18":
        errors.append(f"issueDate is '{draft_inv.get('issueDate')}', expected '2026-03-18'")
    if draft_inv.get("dueDate") != "2026-04-17":
        errors.append(f"dueDate is '{draft_inv.get('dueDate')}', expected '2026-04-17'")

    if errors:
        return False, "; ".join(errors)
    return True, "Prefix set to FINAL-, padding 6, and draft invoice created for Atlas Import/Export Ltd"
