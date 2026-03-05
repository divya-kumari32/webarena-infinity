import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Merino Wool Sweater status is 'archived'."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    products = state.get("products", [])
    sweater = next((p for p in products if "Merino Wool Sweater" in p.get("title", "")), None)
    if not sweater:
        return False, "Product 'Merino Wool Sweater' not found."

    if sweater.get("status") != "archived":
        return False, f"Expected Merino Wool Sweater status to be 'archived', got '{sweater.get('status')}'."

    return True, "Merino Wool Sweater status is 'archived'."
