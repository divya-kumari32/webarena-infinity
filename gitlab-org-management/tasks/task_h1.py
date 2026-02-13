import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that 'community-tools' project was created in Open Source and shared with Product Development."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Step 1: Check project exists in Open Source (group 3)
    open_source_id = 3
    match = [p for p in state["projects"] if p["name"] == "community-tools"]
    if not match:
        return False, "Project 'community-tools' not found."

    project = match[0]
    if project.get("groupId") != open_source_id:
        return False, f"Project is in group {project.get('groupId')}, expected Open Source (id={open_source_id})."

    if project.get("visibility") != "public":
        return False, f"Expected visibility 'public', got '{project.get('visibility')}'."

    # Step 2: Check project share with Product Development (group 2)
    pd_group_id = 2
    project_id = project["id"]

    share = next(
        (
            s
            for s in state["projectShares"]
            if s["sourceGroupId"] == pd_group_id
            and s["targetProjectId"] == project_id
        ),
        None,
    )
    if not share:
        return False, "No project share found from Product Development to 'community-tools'."

    if share.get("maxRole", {}).get("name") != "Developer":
        return False, f"Expected maxRole 'Developer', got '{share.get('maxRole')}'."

    return True, "Project 'community-tools' created in Open Source and shared with Product Development (Developer access)."
