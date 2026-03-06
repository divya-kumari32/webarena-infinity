import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    drafts = [i for i in state["invoices"] if i["status"] == "draft"]
    if drafts:
        draft_nums = ", ".join(i["number"] for i in drafts)
        return False, f"Still {len(drafts)} draft invoice(s): {draft_nums}."

    # Check that at least the known drafts are now awaiting_approval
    for num in ["INV-0058", "INV-0059", "INV-0060"]:
        inv = next((i for i in state["invoices"] if i["number"] == num), None)
        if not inv:
            return False, f"Invoice {num} not found."
        if inv["status"] != "awaiting_approval":
            return False, f"{num} status is '{inv['status']}', expected 'awaiting_approval'."

    return True, "All draft invoices submitted for approval."
