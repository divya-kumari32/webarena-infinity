import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # The overdue invoice with the earliest due date is INV-0046 (Baxter, due 2026-02-01)
    inv = next((i for i in state["invoices"] if i["number"] == "INV-0046"), None)
    if not inv:
        return False, "Invoice INV-0046 not found."

    if inv["status"] != "paid":
        return False, f"INV-0046 status is '{inv['status']}', expected 'paid'."

    if abs(inv["amountDue"]) > 0.01:
        return False, f"INV-0046 amountDue is {inv['amountDue']}, expected 0."

    if not inv.get("payments"):
        return False, "INV-0046 has no payments recorded."

    return True, "INV-0046 (earliest overdue) fully paid."
