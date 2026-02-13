import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that a group named 'DevOps Team' with public visibility was created."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Check that a group named 'DevOps Team' exists
    match = [g for g in state["groups"] if g["name"] == "DevOps Team"]
    if not match:
        return False, "Group 'DevOps Team' not found."

    group = match[0]

    # Check visibility is public
    if group.get("visibility") != "public":
        return False, f"Expected visibility 'public', got '{group.get('visibility')}'."

    # Check that the current user (alex.morgan, id=1) is an Owner of this group
    group_id = group["id"]
    owner_membership = [
        m
        for m in state["groupMemberships"]
        if m["groupId"] == group_id and m["userId"] == 1 and m["role"]["name"] == "Owner"
    ]
    if not owner_membership:
        return False, "Current user (alex.morgan) is not an Owner of the new group."

    return (
        True,
        "Group 'DevOps Team' exists with public visibility and correct Owner membership.",
    )
