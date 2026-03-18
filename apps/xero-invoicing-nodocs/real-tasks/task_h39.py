import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Update the phone number to '+64 0 000 0000' for every contact that has
    at least one voided invoice."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    invoices = state.get("invoices", [])
    contacts = state.get("contacts", [])
    errors = []
    expected_phone = "+64 0 000 0000"

    # Find all contacts that have at least one voided invoice
    voided_contact_ids = set()
    for inv in invoices:
        if inv.get("status") == "voided":
            cid = inv.get("contactId")
            if cid:
                voided_contact_ids.add(cid)

    # Known contacts with voided invoices
    known_contact_ids = {"con_2", "con_18", "con_21", "con_23", "con_24"}

    # Merge both sets to be thorough
    all_expected_ids = voided_contact_ids | known_contact_ids

    if not all_expected_ids:
        errors.append("No contacts with voided invoices found")

    updated_count = 0
    for cid in all_expected_ids:
        contact = next(
            (c for c in contacts if c.get("id") == cid), None
        )
        if contact is None:
            errors.append(f"Contact {cid} not found in contacts list")
            continue
        phone = (contact.get("phone") or "").strip()
        name = contact.get("name", cid)
        if phone != expected_phone:
            errors.append(
                f"Contact '{name}' ({cid}) phone is '{phone}', "
                f"expected '{expected_phone}'"
            )
        else:
            updated_count += 1

    if updated_count == 0 and not errors:
        errors.append("No contacts were verified as updated")

    if errors:
        return False, "Verification failed: " + "; ".join(errors)
    return True, f"Phone updated to '{expected_phone}' for all {updated_count} contacts with voided invoices"
