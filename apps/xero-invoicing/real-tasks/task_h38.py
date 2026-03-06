import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    contact = next((c for c in state["contacts"] if c["name"] == "Northern Territory Power Corp"), None)
    if not contact:
        return False, "Contact Northern Territory Power Corp not found."

    new_inv = next((i for i in state["invoices"]
                    if i["contactId"] == contact["id"]
                    and i["number"] not in ["INV-0064"]
                    and i["status"] == "awaiting_payment"), None)

    if not new_inv:
        return False, "No approved invoice found for Northern Territory Power Corp."

    if not new_inv.get("sentAt"):
        return False, "Invoice has not been sent."

    item_ids = [li.get("itemId") for li in new_inv.get("lineItems", [])]
    if "item_010" not in item_ids:
        return False, "Invoice missing data migration line item."

    if "item_014" not in item_ids:
        return False, "Invoice missing setup fee line item."

    return True, f"Invoice {new_inv['number']} created, approved, and sent for NT Power Corp."
