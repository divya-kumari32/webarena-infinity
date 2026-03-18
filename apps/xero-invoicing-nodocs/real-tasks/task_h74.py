import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Replace REF- with ARCHIVED- and JOB- with COMPLETED- on draft references."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    invoices = state.get("invoices", [])
    errors = []

    archived_count = 0
    completed_count = 0

    for inv in invoices:
        ref = inv.get("reference", "")
        status = inv.get("status")
        inv_num = inv.get("invoiceNumber")

        # Draft invoices should NOT still have REF- or JOB- prefixes
        if status == "draft":
            if ref.startswith("REF-"):
                errors.append(
                    f"{inv_num} (draft) still has reference '{ref}', "
                    f"expected ARCHIVED- prefix"
                )
            if ref.startswith("JOB-"):
                errors.append(
                    f"{inv_num} (draft) still has reference '{ref}', "
                    f"expected COMPLETED- prefix"
                )

        # Check for correctly transformed references
        if ref.startswith("ARCHIVED-"):
            archived_count += 1
        if ref.startswith("COMPLETED-"):
            completed_count += 1

    if errors:
        return False, "; ".join(errors)

    if archived_count == 0:
        return False, "No invoices with ARCHIVED- prefix found"
    if completed_count == 0:
        return False, "No invoices with COMPLETED- prefix found"

    return True, (
        f"References updated: {archived_count} ARCHIVED-, {completed_count} COMPLETED-"
    )
