import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Classic Cotton T-Shirt product status is changed to draft."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    products = state.get("products", [])
    product = next((p for p in products if p["title"] == "Classic Cotton T-Shirt"), None)
    if not product:
        return False, "Product 'Classic Cotton T-Shirt' not found."

    if product.get("status") != "draft":
        return False, f"Expected Classic Cotton T-Shirt status to be 'draft', got '{product.get('status')}'."

    return True, "Classic Cotton T-Shirt product status is draft."
