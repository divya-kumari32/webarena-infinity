import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    contact = next((c for c in state["contacts"] if c["name"] == "CloudNine Analytics"), None)
    if not contact:
        return False, "Contact CloudNine Analytics not found."

    # Find a new credit note for CloudNine with dev hours
    new_cn = next((cn for cn in state["creditNotes"]
                   if cn["contactId"] == contact["id"]
                   and cn["number"] not in ["CN-0008", "CN-0009", "CN-0010", "CN-0011", "CN-0012"]
                   and any(li.get("itemId") == "item_001" for li in cn.get("lineItems", []))), None)

    if not new_cn:
        return False, "No new credit note with dev hours found for CloudNine Analytics."

    dev_line = next((li for li in new_cn["lineItems"] if li.get("itemId") == "item_001"), None)
    if dev_line["quantity"] != 5:
        return False, f"Dev hours quantity is {dev_line['quantity']}, expected 5."

    # Must be approved and allocated
    if not new_cn.get("allocations"):
        return False, "Credit note has no allocations."

    inv = next((i for i in state["invoices"] if i["number"] == "INV-0062"), None)
    if not inv:
        return False, "Invoice INV-0062 not found."

    alloc = next((a for a in new_cn["allocations"] if a["invoiceId"] == inv["id"]), None)
    if not alloc:
        return False, "Credit note not allocated to INV-0062 (CloudNine's smaller invoice)."

    return True, f"Credit note {new_cn['number']} created, approved, and allocated to INV-0062."
