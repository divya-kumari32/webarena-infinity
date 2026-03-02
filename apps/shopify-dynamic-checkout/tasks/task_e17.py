import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    products = state.get("products", [])
    tshirt = next((p for p in products if "Classic Cotton T-Shirt" in p.get("title", "")), None)
    if tshirt is None:
        return False, "Product 'Classic Cotton T-Shirt' not found in state."

    if tshirt.get("status") != "draft":
        return False, f"Expected Classic Cotton T-Shirt status to be 'draft', but got '{tshirt.get('status')}'."

    return True, "Classic Cotton T-Shirt is in draft status."
