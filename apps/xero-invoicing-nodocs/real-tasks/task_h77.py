import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Set branding Minimal Clean, late penalties 1.5% daily, due terms 7,
    then create draft for Swift Courier Services."""
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
    if settings.get("defaultBrandingThemeId") != "theme_3":
        errors.append(
            f"defaultBrandingThemeId is '{settings.get('defaultBrandingThemeId')}', "
            f"expected 'theme_3' (Minimal Clean)"
        )
    if not settings.get("latePenaltyEnabled"):
        errors.append("latePenaltyEnabled is not True")
    if abs((settings.get("latePenaltyRate") or 0) - 1.5) > 0.01:
        errors.append(
            f"latePenaltyRate is {settings.get('latePenaltyRate')}, expected 1.5"
        )
    if settings.get("latePenaltyFrequency") != "daily":
        errors.append(
            f"latePenaltyFrequency is '{settings.get('latePenaltyFrequency')}', "
            f"expected 'daily'"
        )
    if settings.get("defaultDueDateTerms") != "7":
        errors.append(
            f"defaultDueDateTerms is '{settings.get('defaultDueDateTerms')}', expected '7'"
        )

    # Find Swift Courier Services
    scs = next(
        (c for c in contacts if c.get("name") == "Swift Courier Services"), None
    )
    if scs is None:
        return False, "Contact 'Swift Courier Services' not found; " + "; ".join(errors)

    scs_id = scs.get("id")

    # Find draft invoice
    draft_inv = next(
        (inv for inv in invoices
         if inv.get("contactId") == scs_id and inv.get("status") == "draft"
         and inv.get("reference") == "SCS-2026-EXPRESS"),
        None,
    )
    if draft_inv is None:
        errors.append(
            "No draft invoice with reference 'SCS-2026-EXPRESS' found for Swift Courier Services"
        )
        return False, "; ".join(errors)

    # Check line items
    line_items = draft_inv.get("lineItems", [])
    if len(line_items) != 2:
        errors.append(f"Invoice has {len(line_items)} line items, expected 2")

    parcel = next(
        (li for li in line_items
         if "parcel" in (li.get("description") or "").lower()
         or "express" in (li.get("description") or "").lower()),
        None,
    )
    if parcel is None:
        errors.append("No line item containing 'parcel' or 'express'")
    else:
        if parcel.get("quantity") != 50:
            errors.append(f"Express parcel qty is {parcel.get('quantity')}, expected 50")
        if abs((parcel.get("unitPrice") or 0) - 15) > 0.01:
            errors.append(f"Express parcel unitPrice is {parcel.get('unitPrice')}, expected 15")

    freight = next(
        (li for li in line_items
         if "overnight" in (li.get("description") or "").lower()
         or "freight" in (li.get("description") or "").lower()),
        None,
    )
    if freight is None:
        errors.append("No line item containing 'overnight' or 'freight'")
    else:
        if freight.get("quantity") != 10:
            errors.append(f"Overnight freight qty is {freight.get('quantity')}, expected 10")
        if abs((freight.get("unitPrice") or 0) - 95) > 0.01:
            errors.append(f"Overnight freight unitPrice is {freight.get('unitPrice')}, expected 95")

    if draft_inv.get("issueDate") != "2026-03-18":
        errors.append(f"issueDate is '{draft_inv.get('issueDate')}', expected '2026-03-18'")
    if draft_inv.get("dueDate") != "2026-03-25":
        errors.append(f"dueDate is '{draft_inv.get('dueDate')}', expected '2026-03-25'")

    if errors:
        return False, "; ".join(errors)
    return True, "Settings updated and draft invoice created for Swift Courier Services"
