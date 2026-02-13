import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that James Chen's role in Terraform Modules was changed to Owner."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # James Chen is user ID 3, Terraform Modules is group ID 12
    james_id = 3
    tf_group_id = 12

    membership = next(
        (
            m
            for m in state["groupMemberships"]
            if m["groupId"] == tf_group_id and m["userId"] == james_id
        ),
        None,
    )
    if not membership:
        return False, "James Chen has no membership in the Terraform Modules group."

    if membership.get("role", {}).get("name") != "Owner":
        return False, f"Expected role 'Owner', got '{membership.get('role')}'."

    return True, "James Chen's role in Terraform Modules changed to Owner."
