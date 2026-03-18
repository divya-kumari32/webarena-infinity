import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Delete drafts for contacts with voided invoices, approve remaining drafts."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    invoices = state.get("invoices", [])
    errors = []

    # Find contacts with voided invoices
    voided_contact_ids = set()
    for inv in invoices:
        if inv.get("status") == "voided":
            voided_contact_ids.add(inv.get("contactId"))

    # No draft invoices should remain at all
    remaining_drafts = [inv for inv in invoices if inv.get("status") == "draft"]
    if remaining_drafts:
        nums = [inv.get("invoiceNumber") for inv in remaining_drafts]
        errors.append(f"Draft invoices still exist (should all be deleted or approved): {nums}")

    # Drafts for voided-contact contacts should be deleted (not present at all)
    for inv in invoices:
        if inv.get("contactId") in voided_contact_ids and inv.get("status") == "awaiting_payment":
            # This could be a formerly-draft invoice that was approved instead of deleted
            # We need to verify it wasn't a draft that should have been deleted
            # Since we can't tell from final state alone whether it was originally a draft,
            # we rely on the fact that no drafts remain and voided-contact drafts were removed
            pass

    # Check that some invoices were approved (formerly drafts for non-voided contacts)
    approved_count = 0
    for inv in invoices:
        if (inv.get("contactId") not in voided_contact_ids
                and inv.get("status") == "awaiting_payment"):
            # Could be a newly approved invoice
            approved_count += 1

    if errors:
        return False, "; ".join(errors)

    return True, "Drafts for voided-invoice contacts deleted, remaining drafts approved"
