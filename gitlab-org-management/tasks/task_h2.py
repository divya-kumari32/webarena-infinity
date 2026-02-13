import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify subgroup 'Threat Intelligence' under Security with Priya Sharma as Developer."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Step 1: Check subgroup exists under Security (group 4)
    security_id = 4
    match = [g for g in state["groups"] if g["name"] == "Threat Intelligence"]
    if not match:
        return False, "Group 'Threat Intelligence' not found."

    group = match[0]
    if group.get("parentId") != security_id:
        return False, f"Group 'Threat Intelligence' parentId is {group.get('parentId')}, expected {security_id} (Security)."

    # Step 2: Check Priya Sharma (user 2) is a direct Developer member
    priya_id = 2
    group_id = group["id"]

    membership = next(
        (
            m
            for m in state["groupMemberships"]
            if m["groupId"] == group_id
            and m["userId"] == priya_id
            and m.get("membershipType") == "direct"
        ),
        None,
    )
    if not membership:
        return False, "Priya Sharma does not have a direct membership in 'Threat Intelligence'."

    if membership.get("role", {}).get("name") != "Developer":
        return False, f"Expected Priya Sharma's role to be 'Developer', got '{membership.get('role')}'."

    return True, "Subgroup 'Threat Intelligence' created under Security with Priya Sharma as Developer."
