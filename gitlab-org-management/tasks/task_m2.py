import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Emma Wilson was added as Developer to the CI/CD group."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Emma Wilson is user ID 6, CI/CD group is ID 7
    emma_id = 6
    cicd_group_id = 7

    # Verify the user and group exist
    emma = next((u for u in state["users"] if u["id"] == emma_id), None)
    if not emma:
        return False, "User Emma Wilson (id=6) not found."

    cicd = next((g for g in state["groups"] if g["id"] == cicd_group_id), None)
    if not cicd:
        return False, "CI/CD group (id=7) not found."

    # Check for direct membership
    membership = next(
        (
            m
            for m in state["groupMemberships"]
            if m["groupId"] == cicd_group_id
            and m["userId"] == emma_id
            and m.get("membershipType") == "direct"
        ),
        None,
    )
    if not membership:
        return False, "Emma Wilson does not have a direct membership in the CI/CD group."

    if membership.get("role", {}).get("name") != "Developer":
        return False, f"Expected role 'Developer', got '{membership.get('role')}'."

    return True, "Emma Wilson added as Developer to CI/CD group."
