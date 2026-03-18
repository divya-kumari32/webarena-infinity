import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Void the overdue invoice with the earliest due date."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    invoices = state.get("invoices", [])
    errors = []

    # The earliest overdue invoice is INV-0087 with dueDate 2025-10-27
    inv_0087 = next(
        (inv for inv in invoices if inv.get("invoiceNumber") == "INV-0087"),
        None,
    )
    if inv_0087 is None:
        errors.append("INV-0087 not found in invoices")
    else:
        if inv_0087.get("status") != "voided":
            errors.append(
                f"INV-0087 status is '{inv_0087.get('status')}', expected 'voided'"
            )
        voided_at = inv_0087.get("voidedAt")
        if not voided_at:
            errors.append("INV-0087 voidedAt is empty or missing")

    if errors:
        return False, "Verification failed: " + "; ".join(errors)
    return True, "INV-0087 (earliest overdue, due 2025-10-27) successfully voided"
