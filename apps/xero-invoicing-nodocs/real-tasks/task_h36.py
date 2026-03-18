import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Void every overdue invoice that has an empty reference field."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    invoices = state.get("invoices", [])
    errors = []

    # Check no overdue invoices with empty reference remain
    overdue_empty_ref = [
        inv for inv in invoices
        if inv.get("status") == "overdue"
        and (not inv.get("reference") or str(inv.get("reference", "")).strip() == "")
    ]
    if overdue_empty_ref:
        nums = [inv.get("invoiceNumber") for inv in overdue_empty_ref]
        errors.append(f"Overdue invoices with empty reference still exist: {nums}")

    # Verify INV-0068 is voided
    inv_0068 = next(
        (inv for inv in invoices if inv.get("invoiceNumber") == "INV-0068"),
        None,
    )
    if inv_0068 is None:
        errors.append("INV-0068 not found in invoices")
    elif inv_0068.get("status") != "voided":
        errors.append(
            f"INV-0068 status is '{inv_0068.get('status')}', expected 'voided'"
        )

    # Verify INV-0100 is voided
    inv_0100 = next(
        (inv for inv in invoices if inv.get("invoiceNumber") == "INV-0100"),
        None,
    )
    if inv_0100 is None:
        errors.append("INV-0100 not found in invoices")
    elif inv_0100.get("status") != "voided":
        errors.append(
            f"INV-0100 status is '{inv_0100.get('status')}', expected 'voided'"
        )

    if errors:
        return False, "Verification failed: " + "; ".join(errors)
    return True, "All overdue invoices with empty reference have been voided"
