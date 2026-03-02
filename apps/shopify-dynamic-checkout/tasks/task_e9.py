import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    shop_promise = state.get("shopPromise")
    if shop_promise is None:
        return False, "shopPromise not found in state."

    if shop_promise.get("isActive") is not True:
        return False, f"Expected shopPromise isActive to be True, but got {shop_promise.get('isActive')}."

    return True, "Shop Promise is turned on for the store."
