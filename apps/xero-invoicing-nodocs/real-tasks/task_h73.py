import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Update tax ID based on overdue count: SINGLE-OVERDUE or MULTI-OVERDUE."""
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

    # Count overdue invoices per contact
    overdue_counts = {}
    for inv in invoices:
        if inv.get("status") == "overdue":
            cid = inv.get("contactId")
            overdue_counts[cid] = overdue_counts.get(cid, 0) + 1

    single_count = 0
    multi_count = 0

    for con in contacts:
        cid = con.get("id")
        cnt = overdue_counts.get(cid, 0)
        tax_id = con.get("taxId", "")

        if cnt == 1:
            if tax_id != "SINGLE-OVERDUE":
                errors.append(
                    f"{con.get('name')} has 1 overdue invoice but taxId is "
                    f"'{tax_id}', expected 'SINGLE-OVERDUE'"
                )
            else:
                single_count += 1
        elif cnt >= 2:
            if tax_id != "MULTI-OVERDUE":
                errors.append(
                    f"{con.get('name')} has {cnt} overdue invoices but taxId is "
                    f"'{tax_id}', expected 'MULTI-OVERDUE'"
                )
            else:
                multi_count += 1
        else:
            # No overdue — taxId should NOT be changed
            if tax_id in ("SINGLE-OVERDUE", "MULTI-OVERDUE"):
                errors.append(
                    f"{con.get('name')} has no overdue invoices but taxId is '{tax_id}'"
                )

    if errors:
        return False, "; ".join(errors)

    if single_count == 0 and multi_count == 0:
        return False, "No contacts had their taxId updated"

    return True, (
        f"Tax IDs updated: {single_count} SINGLE-OVERDUE, {multi_count} MULTI-OVERDUE"
    )
