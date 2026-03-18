import requests


def verify(server_url: str) -> tuple[bool, str]:
    """On-hold rx (HCTZ) resumed, qty 60, frequency twice daily."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    errors = []

    rx_012 = next((r for r in state["prescriptions"] if r["id"] == "rx_012"), None)
    if not rx_012:
        errors.append("Prescription rx_012 (Hydrochlorothiazide) not found.")
    else:
        if rx_012.get("status") != "active":
            errors.append(f"Expected rx_012 status 'active' (resumed), got '{rx_012.get('status')}'.")
        if rx_012.get("quantity") != 60:
            errors.append(f"Expected rx_012 quantity 60, got {rx_012.get('quantity')}.")
        if rx_012.get("frequency") != "Twice daily":
            errors.append(f"Expected rx_012 frequency 'Twice daily', got '{rx_012.get('frequency')}'.")

    if errors:
        return False, " ".join(errors)
    return True, "HCTZ resumed with quantity 60 and frequency twice daily."
