import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that subgroup 'Performance Testing' was created under Web Application."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Web Application is group ID 9
    web_app_id = 9

    # Find the new group
    match = [g for g in state["groups"] if g["name"] == "Performance Testing"]
    if not match:
        return False, "Group 'Performance Testing' not found."

    group = match[0]
    if group.get("parentId") != web_app_id:
        parent = next(
            (g for g in state["groups"] if g["id"] == group.get("parentId")), None
        )
        parent_name = parent["name"] if parent else "none (top-level)"
        return False, f"Group 'Performance Testing' is under '{parent_name}', expected 'Web Application'."

    # Check that current user (alex.morgan, id=1) is Owner
    owner_membership = next(
        (
            m
            for m in state["groupMemberships"]
            if m["groupId"] == group["id"]
            and m["userId"] == 1
            and m["role"]["name"] == "Owner"
        ),
        None,
    )
    if not owner_membership:
        return False, "Current user is not Owner of the new subgroup."

    return True, "Subgroup 'Performance Testing' created under Web Application with correct ownership."
