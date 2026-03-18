import requests


def verify(server_url: str) -> tuple[bool, str]:
    """JOB- invoices: pay overdue, approve draft, update AP notes."""
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

    paid_count = 0
    approved_count = 0
    notes_count = 0
    expected_notes = "Job complete - pending final review"

    for inv in invoices:
        ref = inv.get("reference", "")
        if "JOB-" not in ref:
            continue

        inv_num = inv.get("invoiceNumber")
        status = inv.get("status")
        inv_id = inv.get("id")

        # Overdue JOB- invoices should now be paid
        if status == "overdue":
            errors.append(
                f"{inv_num} (JOB-, was overdue) still overdue, expected paid"
            )
        elif status == "paid":
            # Verify payment via bank_1
            inv_payments = [p for p in payments if p.get("invoiceId") == inv_id]
            has_bank1 = any(p.get("bankAccountId") == "bank_1" for p in inv_payments)
            if not has_bank1:
                errors.append(f"{inv_num} (JOB-, paid) no payment via bank_1")
            paid_count += 1

        # Draft JOB- invoices should now be approved (awaiting_payment)
        elif status == "draft":
            errors.append(
                f"{inv_num} (JOB-, was draft) still draft, expected approved"
            )
        elif status == "awaiting_payment":
            # Could be a formerly-draft now approved, or an AP with notes
            notes = inv.get("notes", "")
            if notes == expected_notes:
                notes_count += 1
            else:
                # Check if this was approved from draft (activity should show approval)
                activity = inv.get("activity", [])
                has_approval = any(
                    a.get("type") == "approved" for a in activity
                )
                if has_approval:
                    approved_count += 1

    if errors:
        return False, "; ".join(errors)

    if paid_count == 0 and approved_count == 0 and notes_count == 0:
        return False, "No JOB- invoices were processed"

    return True, (
        f"JOB- invoices: {paid_count} paid, {approved_count} approved, "
        f"{notes_count} notes updated"
    )
