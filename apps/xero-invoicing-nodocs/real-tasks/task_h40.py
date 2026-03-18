import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Create contact Aotearoa Digital Agency + create draft invoice with 3
    line items."""
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

    # Find the contact by name
    contact = next(
        (c for c in contacts if c.get("name") == "Aotearoa Digital Agency"),
        None,
    )
    if contact is None:
        return False, "Contact 'Aotearoa Digital Agency' not found"

    contact_id = contact.get("id")

    # Verify contact fields
    if contact.get("email") != "hello@aotearoadigital.co.nz":
        errors.append(
            f"Contact email is '{contact.get('email')}', "
            f"expected 'hello@aotearoadigital.co.nz'"
        )

    if contact.get("phone") != "+64 4 900 1234":
        errors.append(
            f"Contact phone is '{contact.get('phone')}', "
            f"expected '+64 4 900 1234'"
        )

    if contact.get("taxId") != "NZ-99-111-222":
        errors.append(
            f"Contact taxId is '{contact.get('taxId')}', "
            f"expected 'NZ-99-111-222'"
        )

    # Verify billing address
    addr = contact.get("billingAddress", {}) or {}
    expected_addr = {
        "street": "30 Courtenay Place",
        "city": "Wellington",
        "region": "Wellington",
        "postalCode": "6011",
        "country": "New Zealand",
    }
    for field, expected_val in expected_addr.items():
        actual_val = (addr.get(field) or "").strip()
        if actual_val != expected_val:
            errors.append(
                f"Contact billingAddress.{field} is '{actual_val}', "
                f"expected '{expected_val}'"
            )

    # Find a draft invoice for this contact
    draft_inv = next(
        (
            inv for inv in invoices
            if inv.get("contactId") == contact_id
            and inv.get("status") == "draft"
        ),
        None,
    )
    if draft_inv is None:
        errors.append(
            f"No draft invoice found for contact '{contact_id}'"
        )
        return False, "Verification failed: " + "; ".join(errors)

    # Check invoice fields
    if draft_inv.get("issueDate") != "2026-03-18":
        errors.append(
            f"Invoice issueDate is '{draft_inv.get('issueDate')}', "
            f"expected '2026-03-18'"
        )

    if draft_inv.get("dueDate") != "2026-05-17":
        errors.append(
            f"Invoice dueDate is '{draft_inv.get('dueDate')}', "
            f"expected '2026-05-17'"
        )

    if draft_inv.get("reference") != "BRAND-2026-001":
        errors.append(
            f"Invoice reference is '{draft_inv.get('reference')}', "
            f"expected 'BRAND-2026-001'"
        )

    # Check line items
    line_items = draft_inv.get("lineItems", [])
    if len(line_items) != 3:
        errors.append(
            f"Invoice has {len(line_items)} line items, expected 3"
        )

    # Check for brand strategy line item
    brand_strategy = next(
        (
            li for li in line_items
            if "brand strategy" in (li.get("description") or "").lower()
        ),
        None,
    )
    if brand_strategy is None:
        errors.append("No line item with description containing 'brand strategy'")
    else:
        if brand_strategy.get("quantity") != 2:
            errors.append(
                f"Brand strategy quantity is {brand_strategy.get('quantity')}, expected 2"
            )
        if abs((brand_strategy.get("unitPrice", 0) or 0) - 1800) > 0.01:
            errors.append(
                f"Brand strategy unitPrice is {brand_strategy.get('unitPrice')}, expected 1800"
            )

    # Check for logo design line item
    logo_design = next(
        (
            li for li in line_items
            if "logo design" in (li.get("description") or "").lower()
        ),
        None,
    )
    if logo_design is None:
        errors.append("No line item with description containing 'logo design'")
    else:
        if logo_design.get("quantity") != 1:
            errors.append(
                f"Logo design quantity is {logo_design.get('quantity')}, expected 1"
            )
        if abs((logo_design.get("unitPrice", 0) or 0) - 4500) > 0.01:
            errors.append(
                f"Logo design unitPrice is {logo_design.get('unitPrice')}, expected 4500"
            )

    # Check for style guide line item
    style_guide = next(
        (
            li for li in line_items
            if "style guide" in (li.get("description") or "").lower()
        ),
        None,
    )
    if style_guide is None:
        errors.append("No line item with description containing 'style guide'")
    else:
        if style_guide.get("quantity") != 1:
            errors.append(
                f"Style guide quantity is {style_guide.get('quantity')}, expected 1"
            )
        if abs((style_guide.get("unitPrice", 0) or 0) - 2200) > 0.01:
            errors.append(
                f"Style guide unitPrice is {style_guide.get('unitPrice')}, expected 2200"
            )

    if errors:
        return False, "Verification failed: " + "; ".join(errors)
    return True, "Contact 'Aotearoa Digital Agency' created with correct details and draft invoice with 3 line items"
