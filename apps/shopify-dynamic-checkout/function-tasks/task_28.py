import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Hand-Poured Soy Candle Set is archived."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    products = state.get("products", [])

    candle_set = next((p for p in products if p["title"] == "Hand-Poured Soy Candle Set"), None)
    if not candle_set:
        return False, "Product 'Hand-Poured Soy Candle Set' not found."

    if candle_set.get("status") != "archived":
        return False, f"Expected Hand-Poured Soy Candle Set status to be 'archived', got '{candle_set.get('status')}'."

    return True, "Hand-Poured Soy Candle Set is archived."
