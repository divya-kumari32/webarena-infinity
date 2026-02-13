import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify Analytics Platform invited to design-system project with Reporter access and expiry."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Analytics Platform is group ID 14, design-system is project ID 14
    analytics_group_id = 14
    design_system_project_id = 14

    share = next(
        (
            s
            for s in state["projectShares"]
            if s["sourceGroupId"] == analytics_group_id
            and s["targetProjectId"] == design_system_project_id
        ),
        None,
    )
    if not share:
        return False, "No project share found from Analytics Platform to design-system."

    if share.get("maxRole", {}).get("name") != "Reporter":
        return False, f"Expected maxRole 'Reporter', got '{share.get('maxRole')}'."

    expires_at = share.get("expiresAt", "")
    if not expires_at or "2027-06-15" not in expires_at:
        return False, f"Expected expiration containing '2027-06-15', got '{expires_at}'."

    return True, "Analytics Platform invited to design-system with Reporter access, expiring 2027-06-15."
