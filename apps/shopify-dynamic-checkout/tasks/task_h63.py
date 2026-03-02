import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Dawn button bg = Sense primary text, Dawn button text = Sense primary bg, Dawn accent = Ride accent."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])

    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    sense = next((t for t in themes if t.get("name") == "Sense"), None)
    ride = next((t for t in themes if t.get("name") == "Ride"), None)

    if dawn is None:
        return False, "Theme 'Dawn' not found."
    if sense is None:
        return False, "Theme 'Sense' not found."
    if ride is None:
        return False, "Theme 'Ride' not found."

    dawn_colors = dawn.get("settings", {}).get("colors", {})

    # Seed values: Sense primaryText=#3D3D3D, Sense primaryBg=#FFFCF7, Ride accentColor=#3B82F6
    expected_bg = "#3D3D3D"
    expected_text = "#FFFCF7"
    expected_accent = "#3B82F6"

    actual_bg = dawn_colors.get("accentButtonBg", "")
    if actual_bg.upper() != expected_bg.upper():
        return False, (f"Expected Dawn's accent button bg '{expected_bg}' "
                      f"(Sense primary text), got '{actual_bg}'.")

    actual_text = dawn_colors.get("accentButtonText", "")
    if actual_text.upper() != expected_text.upper():
        return False, (f"Expected Dawn's accent button text '{expected_text}' "
                      f"(Sense primary bg), got '{actual_text}'.")

    actual_accent = dawn_colors.get("accentColor", "")
    if actual_accent.upper() != expected_accent.upper():
        return False, (f"Expected Dawn's accent color '{expected_accent}' "
                      f"(Ride accent), got '{actual_accent}'.")

    return True, (f"Dawn button colors set from Sense ({expected_bg}/{expected_text}), "
                  f"accent color set from Ride ({expected_accent}).")
