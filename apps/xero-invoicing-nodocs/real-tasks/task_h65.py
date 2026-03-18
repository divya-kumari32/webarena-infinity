import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Copy INV-0004, change contact to Heritage Craft Brewery, ref HCB-COPY-2026,
    branding Bold Corporate, save as draft."""
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

    # Find Heritage Craft Brewery
    hcb = next(
        (c for c in contacts if c.get("name") == "Heritage Craft Brewery"), None
    )
    if hcb is None:
        return False, "Contact 'Heritage Craft Brewery' not found"

    hcb_id = hcb.get("id")

    # Find the original INV-0004 to get its line items
    orig = next(
        (inv for inv in invoices if inv.get("invoiceNumber") == "INV-0004"), None
    )
    if orig is None:
        return False, "Original invoice INV-0004 not found"

    # Find a draft invoice for Heritage Craft Brewery with ref HCB-COPY-2026
    copy_inv = next(
        (inv for inv in invoices
         if inv.get("contactId") == hcb_id
         and inv.get("status") == "draft"
         and inv.get("reference") == "HCB-COPY-2026"),
        None,
    )
    if copy_inv is None:
        # Try any draft for HCB
        any_draft = next(
            (inv for inv in invoices
             if inv.get("contactId") == hcb_id and inv.get("status") == "draft"),
            None,
        )
        if any_draft is None:
            return False, "No draft invoice found for Heritage Craft Brewery"
        errors.append(
            f"Draft found but reference is '{any_draft.get('reference')}', "
            f"expected 'HCB-COPY-2026'"
        )
        copy_inv = any_draft

    # Check branding theme is Bold Corporate (theme_4)
    if copy_inv.get("brandingThemeId") != "theme_4":
        errors.append(
            f"Branding theme is '{copy_inv.get('brandingThemeId')}', expected 'theme_4' (Bold Corporate)"
        )

    # Check line items match original INV-0004
    orig_items = orig.get("lineItems", [])
    copy_items = copy_inv.get("lineItems", [])

    if len(copy_items) != len(orig_items):
        errors.append(
            f"Copy has {len(copy_items)} line items, expected {len(orig_items)} (matching INV-0004)"
        )
    else:
        for i, (o_li, c_li) in enumerate(zip(orig_items, copy_items)):
            if c_li.get("description") != o_li.get("description"):
                errors.append(
                    f"Line item {i+1} description mismatch: "
                    f"'{c_li.get('description')}' vs '{o_li.get('description')}'"
                )
            if c_li.get("quantity") != o_li.get("quantity"):
                errors.append(
                    f"Line item {i+1} quantity mismatch: "
                    f"{c_li.get('quantity')} vs {o_li.get('quantity')}"
                )
            if abs((c_li.get("unitPrice", 0) or 0) - (o_li.get("unitPrice", 0) or 0)) > 0.01:
                errors.append(
                    f"Line item {i+1} unitPrice mismatch: "
                    f"{c_li.get('unitPrice')} vs {o_li.get('unitPrice')}"
                )

    if errors:
        return False, "; ".join(errors)
    return True, f"INV-0004 copied to Heritage Craft Brewery as draft with ref HCB-COPY-2026 and Bold Corporate theme"
