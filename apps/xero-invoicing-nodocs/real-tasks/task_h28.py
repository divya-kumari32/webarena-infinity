import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Copy INV-0009, change contact to Velocity Sports Equipment, reference VSE-COPY-001, save as draft."""
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

    # Find Velocity Sports Equipment
    velocity = None
    for c in contacts:
        if c.get("name") == "Velocity Sports Equipment":
            velocity = c
            break

    if velocity is None:
        return False, "Contact 'Velocity Sports Equipment' not found"

    velocity_id = velocity.get("id")

    # Find the original INV-0009 to get its line item descriptions
    inv_0009 = None
    for inv in invoices:
        if inv.get("invoiceNumber") == "INV-0009":
            inv_0009 = inv
            break

    if inv_0009 is None:
        return False, "Original invoice INV-0009 not found in state"

    original_descriptions = set()
    for li in inv_0009.get("lineItems", []):
        desc = li.get("description", "")
        if desc:
            original_descriptions.add(desc.lower().strip())

    # Find draft invoice for Velocity Sports with reference VSE-COPY-001
    copied_inv = None
    for inv in invoices:
        if (
            inv.get("contactId") == velocity_id
            and inv.get("reference") == "VSE-COPY-001"
        ):
            copied_inv = inv
            break

    if copied_inv is None:
        # Try finding by just reference
        for inv in invoices:
            if inv.get("reference") == "VSE-COPY-001":
                copied_inv = inv
                errors.append(
                    f"Invoice with reference 'VSE-COPY-001' found but contactId is "
                    f"'{inv.get('contactId')}', expected '{velocity_id}' (Velocity Sports Equipment)"
                )
                break

    if copied_inv is None:
        return False, "No invoice found with reference 'VSE-COPY-001' for Velocity Sports Equipment"

    # Check status is draft
    if copied_inv.get("status") != "draft":
        errors.append(
            f"Copied invoice has status '{copied_inv.get('status')}', expected 'draft'"
        )

    # Check line item descriptions match INV-0009
    copied_descriptions = set()
    for li in copied_inv.get("lineItems", []):
        desc = li.get("description", "")
        if desc:
            copied_descriptions.add(desc.lower().strip())

    if not original_descriptions:
        errors.append("Original INV-0009 has no line items to compare")
    elif not copied_descriptions:
        errors.append("Copied invoice has no line items")
    else:
        # Check that copied invoice contains the same descriptions as original
        missing = original_descriptions - copied_descriptions
        if missing:
            errors.append(
                f"Copied invoice is missing line item description(s) from INV-0009: {missing}"
            )

    if errors:
        return False, "; ".join(errors)

    return True, (
        f"Invoice copied from INV-0009 to Velocity Sports Equipment with reference "
        f"VSE-COPY-001, saved as draft with matching line items"
    )
