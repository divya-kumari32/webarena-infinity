import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    contact = next((c for c in state["contacts"] if c["name"] == "Atlas Engineering Consultants"), None)
    if not contact:
        return False, "Contact Atlas Engineering Consultants not found."

    new_inv = next((i for i in state["invoices"]
                    if i["contactId"] == contact["id"]
                    and i["number"] not in ["INV-0050"]
                    and len(i.get("lineItems", [])) >= 2), None)

    if not new_inv:
        return False, "No new multi-line invoice found for Atlas Engineering."

    design_line = next((li for li in new_inv["lineItems"] if li.get("itemId") == "item_007"), None)
    cable_line = next((li for li in new_inv["lineItems"] if li.get("itemId") == "item_013"), None)

    if not design_line:
        return False, "Invoice missing UI/UX design line item."
    if not cable_line:
        return False, "Invoice missing USB-C cable line item."

    if design_line["quantity"] != 3:
        return False, f"Design hours quantity is {design_line['quantity']}, expected 3."

    if design_line.get("trackingRegion") != "Victoria":
        return False, f"Design line tracking region is '{design_line.get('trackingRegion')}', expected 'Victoria'."

    if design_line.get("trackingDept") != "Sales":
        return False, f"Design line tracking dept is '{design_line.get('trackingDept')}', expected 'Sales'."

    if cable_line["quantity"] != 10:
        return False, f"USB-C cable quantity is {cable_line['quantity']}, expected 10."

    return True, f"Invoice {new_inv['number']} created with tracked design + cables for Atlas Engineering."
