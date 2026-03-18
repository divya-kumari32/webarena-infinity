import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Update phone for contacts with invoices in at least 4 different statuses."""
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

    # Count distinct statuses per contact
    status_sets = {}
    for inv in invoices:
        cid = inv.get("contactId")
        status_sets.setdefault(cid, set()).add(inv.get("status"))

    expected_phone = "+64 800 200 300"
    updated_count = 0

    for con in contacts:
        cid = con.get("id")
        distinct_statuses = len(status_sets.get(cid, set()))
        phone = con.get("phone", "")

        if distinct_statuses >= 4:
            if phone != expected_phone:
                errors.append(
                    f"{con.get('name')} has {distinct_statuses} statuses but phone is "
                    f"'{phone}', expected '{expected_phone}'"
                )
            else:
                updated_count += 1
        else:
            if phone == expected_phone:
                errors.append(
                    f"{con.get('name')} has only {distinct_statuses} statuses but phone "
                    f"was changed to '{expected_phone}'"
                )

    if errors:
        return False, "; ".join(errors)

    if updated_count == 0:
        return False, "No contacts with 4+ statuses had their phone updated"

    return True, f"Phone updated for {updated_count} contact(s) with 4+ invoice statuses"
