import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    contact = next((c for c in state["contacts"] if c["name"] == "Metro Fabrication Works"), None)
    if not contact:
        return False, "Contact Metro Fabrication Works not found."

    new_quo = next((q for q in state["quotes"]
                    if q["contactId"] == contact["id"]
                    and q["number"] not in ["QU-0028"]), None)

    if not new_quo:
        return False, "No new quote found for Metro Fabrication Works."

    if new_quo["status"] != "sent":
        return False, f"Quote status is '{new_quo['status']}', expected 'sent'."

    item_ids = [li.get("itemId") for li in new_quo.get("lineItems", [])]
    if "item_014" not in item_ids:
        return False, "Quote missing setup fee line item."

    if "item_013" not in item_ids:
        return False, "Quote missing USB-C cable line item."

    cable_line = next((li for li in new_quo["lineItems"] if li.get("itemId") == "item_013"), None)
    if cable_line and cable_line["quantity"] != 20:
        return False, f"USB-C cable quantity is {cable_line['quantity']}, expected 20."

    return True, f"Quote {new_quo['number']} created and sent for Metro Fabrication Works."
