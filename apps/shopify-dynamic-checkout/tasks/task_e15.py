import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    products = state.get("products", [])
    candle = next((p for p in products if "Hand-Poured Soy Candle Set" in p.get("title", "")), None)
    if candle is None:
        return False, "Product 'Hand-Poured Soy Candle Set' not found in state."

    if candle.get("status") != "archived":
        return False, f"Expected Hand-Poured Soy Candle Set status to be 'archived', but got '{candle.get('status')}'."

    return True, "Hand-Poured Soy Candle Set is archived."
