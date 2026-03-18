import requests


def verify(server_url: str) -> tuple[bool, str]:
    """3-patient adjustments: David Metoprolol qty 90, Margaret Sertraline twice daily, Robert Carvedilol on hold."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    errors = []

    # rx_016 David's Metoprolol -> quantity 90
    rx_016 = next((r for r in state["prescriptions"] if r["id"] == "rx_016"), None)
    if not rx_016:
        errors.append("Prescription rx_016 (Metoprolol, David) not found.")
    elif rx_016.get("quantity") != 90:
        errors.append(f"Expected rx_016 quantity 90, got {rx_016.get('quantity')}.")

    # rx_013 Margaret's Sertraline -> frequency Twice daily
    rx_013 = next((r for r in state["prescriptions"] if r["id"] == "rx_013"), None)
    if not rx_013:
        errors.append("Prescription rx_013 (Sertraline, Margaret) not found.")
    elif rx_013.get("frequency") != "Twice daily":
        errors.append(f"Expected rx_013 frequency 'Twice daily', got '{rx_013.get('frequency')}'.")

    # rx_028 Robert's Carvedilol -> on-hold
    rx_028 = next((r for r in state["prescriptions"] if r["id"] == "rx_028"), None)
    if not rx_028:
        errors.append("Prescription rx_028 (Carvedilol, Robert) not found.")
    elif rx_028.get("status") != "on-hold":
        errors.append(f"Expected rx_028 (Carvedilol) status 'on-hold', got '{rx_028.get('status')}'.")

    if errors:
        return False, " ".join(errors)
    return True, "All three patients' medications adjusted correctly."
