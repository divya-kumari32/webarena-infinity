import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    contact = next((c for c in state["contacts"] if c["name"] == "Summit Health Group"), None)
    if not contact:
        return False, "Contact Summit Health Group not found."

    new_inv = next((i for i in state["invoices"]
                    if i["contactId"] == contact["id"]
                    and i["number"] not in ["INV-0051"]
                    and len(i.get("lineItems", [])) >= 2), None)

    if not new_inv:
        return False, "No new multi-line invoice found for Summit Health Group."

    dev_line = next((li for li in new_inv["lineItems"] if li.get("itemId") == "item_001"), None)
    pm_line = next((li for li in new_inv["lineItems"] if li.get("itemId") == "item_003"), None)

    if not dev_line:
        return False, "Invoice missing development hours line item."
    if not pm_line:
        return False, "Invoice missing project management line item."

    if dev_line["quantity"] != 20:
        return False, f"Dev hours quantity is {dev_line['quantity']}, expected 20."

    if abs(dev_line.get("discountPercent", 0) - 15) > 0.5:
        return False, f"Dev hours discount is {dev_line.get('discountPercent')}%, expected 15%."

    if pm_line["quantity"] != 2:
        return False, f"PM days quantity is {pm_line['quantity']}, expected 2."

    return True, f"Invoice {new_inv['number']} created for Summit Health Group with discounted dev + PM."
