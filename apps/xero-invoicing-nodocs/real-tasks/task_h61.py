import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Void the overdue invoice with the second-highest total amount."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    invoices = state.get("invoices", [])

    # Find all overdue invoices (some may now be voided if task was done)
    # We need to identify which one SHOULD have been voided
    # Strategy: collect all invoices that are overdue OR were the 2nd-highest and now voided
    overdue_candidates = [
        inv for inv in invoices
        if inv.get("status") in ("overdue", "voided")
    ]

    if len(overdue_candidates) < 2:
        return False, "Not enough overdue/voided invoices to determine second-highest"

    # Sort by total descending
    overdue_candidates.sort(key=lambda i: i.get("total", 0), reverse=True)

    # The second-highest total invoice
    second_highest = overdue_candidates[1]
    inv_num = second_highest.get("invoiceNumber")

    if second_highest.get("status") != "voided":
        return False, (
            f"Invoice {inv_num} (second-highest total overdue) "
            f"has status '{second_highest.get('status')}', expected 'voided'"
        )

    # Make sure the highest was NOT voided (only second should be voided)
    highest = overdue_candidates[0]
    if highest.get("status") == "voided":
        return False, (
            f"Invoice {highest.get('invoiceNumber')} (highest total) was also voided — "
            f"only the second-highest should be voided"
        )

    return True, f"Invoice {inv_num} (second-highest total overdue) has been voided"
