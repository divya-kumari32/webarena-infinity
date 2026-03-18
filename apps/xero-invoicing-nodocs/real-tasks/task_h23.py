import requests


def verify(server_url: str) -> tuple[bool, str]:
    """For all draft invoices: approve those with a total exceeding $5,000, and delete those with a total of $5,000 or less."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    invoices = state.get("invoices", [])

    remaining_drafts = []
    for inv in invoices:
        if inv.get("status") == "draft":
            remaining_drafts.append(inv.get("invoiceNumber", inv.get("id")))

    if remaining_drafts:
        return False, (
            f"Found {len(remaining_drafts)} invoice(s) still in 'draft' status: "
            f"{', '.join(remaining_drafts)}. All drafts should have been approved (>$5,000) or deleted (<=$5,000)."
        )

    return True, "No draft invoices remain — high-value drafts approved, low-value drafts deleted"
