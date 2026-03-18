import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Prepend 'archived-' to email for contacts with voided invoices."""
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

    # Find contact IDs with voided invoices
    voided_contact_ids = set()
    for inv in invoices:
        if inv.get("status") == "voided":
            voided_contact_ids.add(inv.get("contactId"))

    if not voided_contact_ids:
        return False, "No voided invoices found in state"

    updated_count = 0
    for con in contacts:
        cid = con.get("id")
        email = con.get("email", "")

        if cid in voided_contact_ids:
            if not email.startswith("archived-"):
                errors.append(
                    f"{con.get('name')} has voided invoices but email "
                    f"'{email}' does not start with 'archived-'"
                )
            elif "@" not in email[len("archived-"):]:
                errors.append(
                    f"{con.get('name')} email '{email}' appears malformed after prepending"
                )
            else:
                updated_count += 1
        else:
            # Contacts without voided invoices should NOT have archived- prefix
            if email.startswith("archived-"):
                errors.append(
                    f"{con.get('name')} has no voided invoices but email "
                    f"starts with 'archived-': '{email}'"
                )

    if errors:
        return False, "; ".join(errors)

    if updated_count == 0:
        return False, "No contacts with voided invoices had their email updated"

    return True, f"Email prepended with 'archived-' for {updated_count} contact(s) with voided invoices"
