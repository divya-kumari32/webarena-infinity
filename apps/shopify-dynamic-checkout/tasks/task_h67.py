import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Publish Ride, copy Taste colors to Ride, set Ride fonts."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])

    ride = next((t for t in themes if t.get("name") == "Ride"), None)
    taste = next((t for t in themes if t.get("name") == "Taste"), None)
    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)

    if ride is None:
        return False, "Theme 'Ride' not found."
    if taste is None:
        return False, "Theme 'Taste' not found."

    # Check Ride is published
    if ride.get("role") != "main":
        return False, f"Expected Ride published (role='main'), got '{ride.get('role')}'."

    # Dawn should no longer be published
    if dawn and dawn.get("role") == "main":
        return False, "Dawn should no longer be published."

    # Taste seed colors (these should now be on Ride)
    taste_seed_colors = {
        "accentButtonBg": "#7C3AED",
        "accentButtonText": "#FFFFFF",
        "primaryBg": "#FAFAFA",
        "primaryText": "#18181B",
        "secondaryBg": "#F4F4F5",
        "secondaryText": "#52525B",
        "accentColor": "#7C3AED"
    }

    ride_colors = ride.get("settings", {}).get("colors", {})
    for key, expected in taste_seed_colors.items():
        actual = ride_colors.get(key, "")
        if actual.upper() != expected.upper():
            return False, (f"Expected Ride {key}='{expected}' (from Taste), "
                          f"got '{actual}'.")

    # Check Ride typography
    ride_typo = ride.get("settings", {}).get("typography", {})
    if ride_typo.get("headingFont") != "Oswald":
        return False, f"Expected Ride heading font 'Oswald', got '{ride_typo.get('headingFont')}'."
    if ride_typo.get("bodyFont") != "Raleway":
        return False, f"Expected Ride body font 'Raleway', got '{ride_typo.get('bodyFont')}'."
    if ride_typo.get("buttonFont") != "Oswald":
        return False, f"Expected Ride button font 'Oswald', got '{ride_typo.get('buttonFont')}'."

    return True, ("Ride published. Taste color scheme applied to Ride. "
                  "Ride fonts: Oswald/Raleway/Oswald.")
