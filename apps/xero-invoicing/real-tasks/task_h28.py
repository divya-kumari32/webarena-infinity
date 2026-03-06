import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    contact = next((c for c in state["contacts"] if c["name"] == "Outback Adventures Tourism"), None)
    if not contact:
        return False, "Contact Outback Adventures Tourism not found."

    ri = next((r for r in state["repeatingInvoices"]
               if r["contactId"] == contact["id"]), None)

    if not ri:
        return False, "No repeating invoice found for Outback Adventures Tourism."

    if ri["frequency"] != "fortnightly":
        return False, f"Frequency is '{ri['frequency']}', expected 'fortnightly'."

    if ri["saveAs"] != "approved":
        return False, f"Save-as is '{ri['saveAs']}', expected 'approved' (auto-approved)."

    item_ids = [li.get("itemId") for li in ri.get("lineItems", [])]
    if "item_007" not in item_ids:
        return False, "Repeating invoice missing UI/UX design line item."

    return True, f"Fortnightly auto-approved repeating invoice set up for Outback Adventures."
