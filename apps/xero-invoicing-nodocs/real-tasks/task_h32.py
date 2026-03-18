import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Send all invoices currently awaiting approval, then change the default
    due date terms to 60 days."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    invoices = state.get("invoices", [])
    settings = state.get("settings", {})
    errors = []

    # Check no invoices with status "awaiting_approval" remain
    awaiting = [
        inv for inv in invoices
        if inv.get("status") == "awaiting_approval"
    ]
    if awaiting:
        nums = [inv.get("invoiceNumber") for inv in awaiting]
        errors.append(f"Invoices still awaiting approval: {nums}")

    # Check default due date terms is "60"
    due_date_terms = str(settings.get("defaultDueDateTerms", ""))
    if due_date_terms != "60":
        errors.append(
            f"Default due date terms is '{due_date_terms}', expected '60'"
        )

    if errors:
        return False, "Verification failed: " + "; ".join(errors)
    return True, "All awaiting-approval invoices sent and default due date terms set to 60 days"
