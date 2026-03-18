import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Update postal code to 1142 for Auckland contacts with outstanding > $3,000."""
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

    # Compute outstanding balance per contact
    balances = {}
    for inv in invoices:
        if inv.get("status") in ("awaiting_payment", "overdue"):
            cid = inv.get("contactId")
            balances[cid] = balances.get(cid, 0) + inv.get("amountDue", 0)

    updated_count = 0

    for con in contacts:
        cid = con.get("id")
        addr = con.get("billingAddress", {})
        city = addr.get("city", "")
        region = addr.get("region", "")
        balance = balances.get(cid, 0)

        # Auckland-based contacts
        if city == "Auckland" or region == "Auckland":
            postal = addr.get("postalCode", "")
            if balance > 3000:
                if postal != "1142":
                    errors.append(
                        f"{con.get('name')} (Auckland, balance ${balance:.2f}) "
                        f"postal code is '{postal}', expected '1142'"
                    )
                else:
                    updated_count += 1
            else:
                # Should NOT have been changed to 1142
                if postal == "1142":
                    errors.append(
                        f"{con.get('name')} (Auckland, balance ${balance:.2f} <= $3,000) "
                        f"postal code was changed to '1142' but should not have been"
                    )

    if errors:
        return False, "; ".join(errors)

    if updated_count == 0:
        return False, "No Auckland contacts with balance > $3,000 had postal code updated"

    return True, f"Postal code updated to 1142 for {updated_count} Auckland contact(s) with balance > $3,000"
