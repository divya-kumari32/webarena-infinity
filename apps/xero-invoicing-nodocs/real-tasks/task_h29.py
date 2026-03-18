import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Update billing region for all Bay of Plenty contacts to 'BOP'."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    contacts = state.get("contacts", [])

    # The Bay of Plenty contacts in seed data:
    # con_9: Pinnacle Construction Co (Tauranga, Bay of Plenty)
    # con_14: Pacific Timber Supplies (Rotorua, Bay of Plenty)
    bop_contact_names = {
        "Pinnacle Construction Co": "con_9",
        "Pacific Timber Supplies": "con_14",
    }

    errors = []
    checked = 0

    for name, expected_id in bop_contact_names.items():
        contact = None
        for c in contacts:
            if c.get("name") == name:
                contact = c
                break

        if contact is None:
            errors.append(f"Contact '{name}' not found in state")
            continue

        checked += 1
        addr = contact.get("billingAddress", {})
        region = addr.get("region")
        if region != "BOP":
            errors.append(
                f"Contact '{name}' has billingAddress.region='{region}', expected 'BOP'"
            )

    if errors:
        return False, "; ".join(errors)

    if checked == 0:
        return False, "No Bay of Plenty contacts found to check"

    return True, (
        f"All Bay of Plenty contacts ({checked}) have billingAddress.region updated to 'BOP'"
    )
