import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    contact = next((c for c in state["contacts"] if c["name"] == "Harbour City Plumbing"), None)
    if not contact:
        return False, "Contact Harbour City Plumbing not found."

    new_inv = next((i for i in state["invoices"]
                    if i["contactId"] == contact["id"]
                    and i["status"] == "awaiting_payment"), None)

    if not new_inv:
        return False, "No approved invoice found for Harbour City Plumbing."

    if new_inv["brandingThemeId"] != "theme_professional":
        return False, f"Template is '{new_inv['brandingThemeId']}', expected Professional Services."

    item_ids = [li.get("itemId") for li in new_inv.get("lineItems", [])]
    if "item_009" not in item_ids:
        return False, "Invoice missing security audit line item."

    if "item_001" not in item_ids:
        return False, "Invoice missing development hours line item."

    dev_line = next((li for li in new_inv["lineItems"] if li.get("itemId") == "item_001"), None)
    if dev_line and dev_line["quantity"] != 16:
        return False, f"Dev hours quantity is {dev_line['quantity']}, expected 16."

    return True, f"Approved invoice {new_inv['number']} created for Harbour City Plumbing."
