import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Non-Mitchell rxs: family med renewed 6, internal med on hold, cardiology qty 120."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    errors = []

    # rx_004 Levothyroxine (prov_002 Okafor, Family Medicine) -> renewed with 6 refills
    rx_004 = next((r for r in state["prescriptions"] if r["id"] == "rx_004"), None)
    if not rx_004:
        errors.append("Prescription rx_004 (Levothyroxine) not found.")
    elif rx_004.get("refillsRemaining") != 6:
        errors.append(f"Expected rx_004 (Levothyroxine, Dr. Okafor) refillsRemaining 6, got {rx_004.get('refillsRemaining')}.")

    # rx_007 Gabapentin (prov_003 Reyes, Internal Medicine) -> on-hold
    rx_007 = next((r for r in state["prescriptions"] if r["id"] == "rx_007"), None)
    if not rx_007:
        errors.append("Prescription rx_007 (Gabapentin) not found.")
    elif rx_007.get("status") != "on-hold":
        errors.append(f"Expected rx_007 (Gabapentin, Dr. Reyes) status 'on-hold', got '{rx_007.get('status')}'.")

    # rx_014 Apixaban (prov_006 Tanaka, Cardiology) -> quantity 120
    rx_014 = next((r for r in state["prescriptions"] if r["id"] == "rx_014"), None)
    if not rx_014:
        errors.append("Prescription rx_014 (Apixaban) not found.")
    elif rx_014.get("quantity") != 120:
        errors.append(f"Expected rx_014 (Apixaban, Dr. Tanaka) quantity 120, got {rx_014.get('quantity')}.")

    if errors:
        return False, " ".join(errors)
    return True, "Non-Mitchell prescriptions updated: Levothyroxine renewed, Gabapentin on hold, Apixaban qty 120."
