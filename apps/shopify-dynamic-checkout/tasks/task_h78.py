import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Stride Lab product with lowest total inventory → draft, disable template checkout."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    templates = state.get("templates", [])
    products = state.get("products", [])

    # In seed data, Stride Lab products and total inventories:
    # Canvas Sneakers: 431, Titanium Watch: 29, Yoga Pants: 493,
    # Running Shorts: 423, Base Layer: 295
    # Lowest = Titanium Watch (29 units)

    watch = next((p for p in products
                  if "Titanium Watch" in p.get("title", "")), None)
    if watch is None:
        return False, "Titanium Watch not found."

    if watch.get("status") != "draft":
        return False, (f"Expected Titanium Watch (lowest Stride Lab inventory) "
                      f"to be draft, got status='{watch.get('status')}'.")

    # The watch was on tmpl_1 (Dawn default). Check its template has checkout disabled.
    tmpl_id = watch.get("templateId")
    tmpl = next((t for t in templates if t.get("id") == tmpl_id), None)
    if tmpl is None:
        return False, f"Template '{tmpl_id}' not found."

    if tmpl.get("showAcceleratedCheckout") is not False:
        return False, (f"Expected template '{tmpl['name']}' checkout disabled, "
                      f"got {tmpl.get('showAcceleratedCheckout')}.")

    return True, ("Titanium Watch (lowest Stride Lab inventory: 29 units) set to draft. "
                  f"Template '{tmpl['name']}' checkout disabled.")
