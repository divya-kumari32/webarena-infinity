import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # The client with the highest awaiting-payment invoice is TechVault (INV-0055, $41,800)
    contact = next((c for c in state["contacts"] if c["name"] == "TechVault Solutions Pty Ltd"), None)
    if not contact:
        return False, "Contact TechVault Solutions not found."

    new_quo = next((q for q in state["quotes"]
                    if q["contactId"] == contact["id"]
                    and q["status"] == "sent"), None)

    if not new_quo:
        return False, "No sent quote found for TechVault Solutions."

    consult_line = next((li for li in new_quo.get("lineItems", [])
                         if li.get("itemId") == "item_002"), None)

    if not consult_line:
        return False, "Quote missing consulting services line item."

    if consult_line["quantity"] != 10:
        return False, f"Consulting quantity is {consult_line['quantity']}, expected 10."

    return True, f"Sent quote {new_quo['number']} for 10 hrs consulting to TechVault."
