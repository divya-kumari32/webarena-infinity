import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify Liam O'Shea removed and Sofia Petrov added as Developer to web-frontend."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # web-frontend is project ID 6
    # Liam O'Shea is user ID 7, Sofia Petrov is user ID 9
    project_id = 6
    liam_id = 7
    sofia_id = 9

    # Check Liam is no longer a direct project member
    liam_membership = next(
        (
            m
            for m in state["projectMemberships"]
            if m["projectId"] == project_id and m["userId"] == liam_id
        ),
        None,
    )
    if liam_membership:
        return False, "Liam O'Shea still has a direct membership in web-frontend."

    # Check Sofia is a direct project member with Developer role
    sofia_membership = next(
        (
            m
            for m in state["projectMemberships"]
            if m["projectId"] == project_id and m["userId"] == sofia_id
        ),
        None,
    )
    if not sofia_membership:
        return False, "Sofia Petrov does not have a direct membership in web-frontend."

    if sofia_membership.get("role", {}).get("name") != "Developer":
        return False, f"Expected Sofia Petrov's role to be 'Developer', got '{sofia_membership.get('role')}'."

    return True, "Liam O'Shea removed and Sofia Petrov added as Developer to web-frontend."
