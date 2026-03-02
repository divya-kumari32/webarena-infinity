import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Shop Promise is enabled."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    shop_promise = state.get("shopPromise")
    if not shop_promise:
        return False, "shopPromise not found in state."

    if shop_promise.get("isActive") is not True:
        return False, f"Expected shopPromise.isActive to be true, got '{shop_promise.get('isActive')}'."

    return True, "Shop Promise is enabled."
