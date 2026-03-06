import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # The most expensive paid invoice is INV-0064 (NT Power Corp, $23,100)
    src = next((i for i in state["invoices"] if i["number"] == "INV-0064"), None)
    if not src:
        return False, "Source invoice INV-0064 not found."

    # Find a new draft invoice with the same contact and total
    new_inv = next((i for i in state["invoices"]
                    if i["contactId"] == src["contactId"]
                    and i["number"] != "INV-0064"
                    and i["status"] == "draft"
                    and abs(i["total"] - src["total"]) < 0.01), None)

    if not new_inv:
        return False, "No draft copy of INV-0064 found."

    if len(new_inv.get("lineItems", [])) != len(src.get("lineItems", [])):
        return False, f"Copy has {len(new_inv['lineItems'])} line items, expected {len(src['lineItems'])}."

    return True, f"INV-0064 duplicated as {new_inv['number']}."
