import requests


def verify(server_url: str) -> tuple[bool, str]:
    """For all overdue invoices whose reference starts with 'PO-', void them.
    For all overdue invoices whose reference starts with 'JOB-', record a full
    payment via the Business Cheque Account."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    invoices = state.get("invoices", [])
    payments = state.get("payments", [])
    errors = []

    # Check no overdue invoices with PO- reference remain
    po_overdue = [
        inv for inv in invoices
        if inv.get("status") == "overdue"
        and isinstance(inv.get("reference", ""), str)
        and inv.get("reference", "").startswith("PO-")
    ]
    if po_overdue:
        nums = [inv.get("invoiceNumber") for inv in po_overdue]
        errors.append(f"Overdue invoices with PO- reference still exist: {nums}")

    # Check no overdue invoices with JOB- reference remain
    job_overdue = [
        inv for inv in invoices
        if inv.get("status") == "overdue"
        and isinstance(inv.get("reference", ""), str)
        and inv.get("reference", "").startswith("JOB-")
    ]
    if job_overdue:
        nums = [inv.get("invoiceNumber") for inv in job_overdue]
        errors.append(f"Overdue invoices with JOB- reference still exist: {nums}")

    # Verify INV-0102 is voided
    inv_0102 = next((inv for inv in invoices if inv.get("invoiceNumber") == "INV-0102"), None)
    if inv_0102 is None:
        errors.append("INV-0102 not found in invoices")
    elif inv_0102.get("status") != "voided":
        errors.append(f"INV-0102 status is '{inv_0102.get('status')}', expected 'voided'")

    # Verify INV-0033 is paid with amountDue <= 0.01 and payment via bank_1
    inv_0033 = next((inv for inv in invoices if inv.get("invoiceNumber") == "INV-0033"), None)
    if inv_0033 is None:
        errors.append("INV-0033 not found in invoices")
    else:
        if inv_0033.get("status") != "paid":
            errors.append(f"INV-0033 status is '{inv_0033.get('status')}', expected 'paid'")
        if inv_0033.get("amountDue", 999) > 0.01:
            errors.append(f"INV-0033 amountDue is {inv_0033.get('amountDue')}, expected <= 0.01")
        inv_0033_payments = [p for p in payments if p.get("invoiceId") == inv_0033.get("id")]
        bank_ids_0033 = [p.get("bankAccountId") for p in inv_0033_payments]
        if "bank_1" not in bank_ids_0033:
            errors.append(f"INV-0033 has no payment with bankAccountId 'bank_1'. Payment bank IDs: {bank_ids_0033}")

    # Verify INV-0059 is paid with amountDue <= 0.01 and payment via bank_1
    inv_0059 = next((inv for inv in invoices if inv.get("invoiceNumber") == "INV-0059"), None)
    if inv_0059 is None:
        errors.append("INV-0059 not found in invoices")
    else:
        if inv_0059.get("status") != "paid":
            errors.append(f"INV-0059 status is '{inv_0059.get('status')}', expected 'paid'")
        if inv_0059.get("amountDue", 999) > 0.01:
            errors.append(f"INV-0059 amountDue is {inv_0059.get('amountDue')}, expected <= 0.01")
        inv_0059_payments = [p for p in payments if p.get("invoiceId") == inv_0059.get("id")]
        bank_ids_0059 = [p.get("bankAccountId") for p in inv_0059_payments]
        if "bank_1" not in bank_ids_0059:
            errors.append(f"INV-0059 has no payment with bankAccountId 'bank_1'. Payment bank IDs: {bank_ids_0059}")

    if errors:
        return False, "Verification failed: " + "; ".join(errors)
    return True, "All PO- overdue invoices voided and all JOB- overdue invoices paid via Business Cheque Account"
