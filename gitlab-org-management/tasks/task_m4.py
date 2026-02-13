import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Open Source group was invited to Product Development with Reporter max role."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Open Source is group ID 3 (source), Product Development is group ID 2 (target)
    source_group_id = 3
    target_group_id = 2

    share = next(
        (
            s
            for s in state["groupShares"]
            if s["sourceGroupId"] == source_group_id
            and s["targetGroupId"] == target_group_id
        ),
        None,
    )
    if not share:
        return False, "No group share found from 'Open Source' to 'Product Development'."

    if share.get("maxRole", {}).get("name") != "Reporter":
        return False, f"Expected maxRole 'Reporter', got '{share.get('maxRole')}'."

    return True, "Open Source group invited to Product Development with Reporter max role."
