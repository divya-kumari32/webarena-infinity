import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Quote must be accepted
    quo = next((q for q in state["quotes"] if q["number"] == "QU-0023"), None)
    if not quo:
        return False, "Quote QU-0023 not found."

    if quo["status"] != "accepted":
        return False, f"QU-0023 status is '{quo['status']}', expected 'accepted'."

    if not quo.get("isInvoiced"):
        return False, "QU-0023 is not marked as invoiced."

    # A new invoice should exist for the same contact
    contact_id = quo["contactId"]
    new_inv = next((i for i in state["invoices"]
                    if i["contactId"] == contact_id
                    and i["number"] not in ["INV-0060"]), None)

    if not new_inv:
        return False, "No new invoice found for Redback Mining Supplies."

    if abs(new_inv["total"] - quo["total"]) > 0.01:
        return False, f"New invoice total {new_inv['total']} doesn't match quote total {quo['total']}."

    return True, f"QU-0023 accepted and converted to invoice {new_inv['number']}."
