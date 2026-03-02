import requests
from collections import Counter


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("installedApps", [])

    # Find apps that share the same conflict reason
    # In seed data: ReConvert and CartHook both have
    # "Apps that interact with the cart may conflict with accelerated checkout."
    reason_groups = {}
    for app in apps:
        reason = app.get("conflictReason")
        if reason:
            reason_groups.setdefault(reason, []).append(app)

    shared_reason_pairs = {r: group for r, group in reason_groups.items() if len(group) == 2}
    if not shared_reason_pairs:
        return False, "No pair of apps with the same conflict reason found."

    # Get the pair
    for reason, pair in shared_reason_pairs.items():
        # The originally active one should now be inactive
        # The originally inactive one should now be active
        reconvert = next((a for a in pair if a.get("name") == "ReConvert Upsell & Cross Sell"), None)
        carthook = next((a for a in pair if "CartHook" in a.get("name", "")), None)

        if reconvert is None or carthook is None:
            return False, "Expected ReConvert and CartHook to share a conflict reason."

        if reconvert.get("isActive") is not False:
            return False, (
                f"Expected ReConvert Upsell & Cross Sell to be deactivated "
                f"(it was the active one), but got isActive={reconvert.get('isActive')}."
            )

        if carthook.get("isActive") is not True:
            return False, (
                f"Expected CartHook Post Purchase Offers to be activated "
                f"(it was the inactive one), but got isActive={carthook.get('isActive')}."
            )

    return True, (
        "ReConvert (originally active) deactivated and CartHook (originally inactive) activated — "
        "apps sharing the same conflict reason swapped."
    )
