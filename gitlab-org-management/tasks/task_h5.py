import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify Omar Hassan added as Maintainer to Terraform Modules with expiry 2027-12-31."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Omar Hassan is user ID 5, Terraform Modules is group ID 12
    omar_id = 5
    tf_group_id = 12

    membership = next(
        (
            m
            for m in state["groupMemberships"]
            if m["groupId"] == tf_group_id
            and m["userId"] == omar_id
            and m.get("membershipType") == "direct"
        ),
        None,
    )
    if not membership:
        return False, "Omar Hassan does not have a direct membership in Terraform Modules."

    if membership.get("role", {}).get("name") != "Maintainer":
        return False, f"Expected role 'Maintainer', got '{membership.get('role')}'."

    expires_at = membership.get("expiresAt", "")
    if not expires_at or "2027-12-31" not in expires_at:
        return False, f"Expected expiration containing '2027-12-31', got '{expires_at}'."

    return True, "Omar Hassan added as Maintainer to Terraform Modules with expiry 2027-12-31."
