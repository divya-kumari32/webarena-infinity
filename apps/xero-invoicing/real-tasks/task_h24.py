import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    cn = next((c for c in state["creditNotes"] if c["number"] == "CN-0011"), None)
    if not cn:
        return False, "Credit note CN-0011 not found."

    # Must be approved (not draft)
    if cn["status"] == "draft":
        return False, "CN-0011 is still in draft status (not approved)."

    inv = next((i for i in state["invoices"] if i["number"] == "INV-0048"), None)
    if not inv:
        return False, "Invoice INV-0048 not found."

    if not cn.get("allocations"):
        return False, "CN-0011 has no allocations."

    alloc = next((a for a in cn["allocations"] if a["invoiceId"] == inv["id"]), None)
    if not alloc:
        return False, "CN-0011 not allocated to INV-0048."

    if abs(alloc["amount"] - 968.00) > 0.01:
        return False, f"Allocation amount is {alloc['amount']}, expected 968.00."

    return True, "CN-0011 approved and allocated to INV-0048 (Pacific Freight Lines)."
