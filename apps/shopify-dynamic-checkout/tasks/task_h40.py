import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])

    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found."

    sense = next((t for t in themes if t.get("name") == "Sense"), None)
    if sense is None:
        return False, "Theme 'Sense' not found."

    dawn_colors = dawn.get("settings", {}).get("colors", {})
    sense_colors = sense.get("settings", {}).get("colors", {})

    # Dawn's original primaryText (#1A1A1A) should now be Sense's accentButtonBg
    expected_sense_bg = "#1A1A1A"
    actual_sense_bg = sense_colors.get("accentButtonBg", "")
    if actual_sense_bg.upper() != expected_sense_bg.upper():
        return False, (
            f"Expected Sense accentButtonBg to be '{expected_sense_bg}' "
            f"(Dawn's primary text color), but got '{actual_sense_bg}'."
        )

    # Sense's original accentColor (#C8553D) should now be Dawn's accentColor
    expected_dawn_accent = "#C8553D"
    actual_dawn_accent = dawn_colors.get("accentColor", "")
    if actual_dawn_accent.upper() != expected_dawn_accent.upper():
        return False, (
            f"Expected Dawn accentColor to be '{expected_dawn_accent}' "
            f"(Sense's accent color), but got '{actual_dawn_accent}'."
        )

    return True, (
        "Sense accentButtonBg set to Dawn's primary text (#1A1A1A), "
        "Dawn accentColor set to Sense's accent (#C8553D)."
    )
