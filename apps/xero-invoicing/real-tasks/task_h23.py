import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # CloudNine's earliest-due invoice is INV-0047 (due 2026-02-15)
    inv = next((i for i in state["invoices"] if i["number"] == "INV-0047"), None)
    if not inv:
        return False, "Invoice INV-0047 not found."

    if inv["status"] != "paid":
        return False, f"INV-0047 status is '{inv['status']}', expected 'paid'."

    if abs(inv["amountDue"]) > 0.01:
        return False, f"INV-0047 amountDue is {inv['amountDue']}, expected 0."

    if not inv.get("payments"):
        return False, "INV-0047 has no payments recorded."

    return True, "INV-0047 (CloudNine's earliest-due invoice) fully paid."
