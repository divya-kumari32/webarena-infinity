import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Margaret's IR Metformin discontinued, David's ER Metformin on hold."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    errors = []

    # rx_003 Margaret's Metformin 1000mg Tablet (IR) -> discontinued
    rx_003 = next((r for r in state["prescriptions"] if r["id"] == "rx_003"), None)
    if not rx_003:
        errors.append("Prescription rx_003 (Metformin IR, Margaret) not found.")
    elif rx_003.get("status") != "discontinued":
        errors.append(f"Expected rx_003 (Metformin IR) status 'discontinued', got '{rx_003.get('status')}'.")

    # rx_019 David's Metformin 500mg Tablet ER -> on-hold
    rx_019 = next((r for r in state["prescriptions"] if r["id"] == "rx_019"), None)
    if not rx_019:
        errors.append("Prescription rx_019 (Metformin ER, David) not found.")
    elif rx_019.get("status") != "on-hold":
        errors.append(f"Expected rx_019 (Metformin ER) status 'on-hold', got '{rx_019.get('status')}'.")

    if errors:
        return False, " ".join(errors)
    return True, "Margaret's IR Metformin discontinued, David's ER Metformin on hold."
