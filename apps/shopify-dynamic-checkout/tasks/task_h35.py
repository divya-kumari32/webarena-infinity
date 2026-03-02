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

    # Find unpublished theme with highest heading scale
    # In seed data: Craft=110, Sense=120, Ride=105, Taste=100
    # Sense has 120 (highest)
    unpublished = [t for t in themes if t.get("role") == "unpublished"]
    if not unpublished:
        return False, "No unpublished themes found."

    highest = max(unpublished, key=lambda t: t.get("settings", {}).get("typography", {}).get("headingScale", 0))
    highest_name = highest["name"]
    source_colors = highest.get("settings", {}).get("colors", {})

    dawn_colors = dawn.get("settings", {}).get("colors", {})

    # Check all 7 color values match
    color_keys = [
        "accentButtonBg", "accentButtonText", "primaryBg", "primaryText",
        "secondaryBg", "secondaryText", "accentColor"
    ]
    for key in color_keys:
        expected = source_colors.get(key, "")
        actual = dawn_colors.get(key, "")
        if actual.upper() != expected.upper():
            return False, (
                f"Dawn's {key} should be '{expected}' (from {highest_name}), "
                f"but got '{actual}'."
            )

    return True, (
        f"Dawn's complete color scheme copied from '{highest_name}' "
        f"(unpublished theme with highest heading scale of "
        f"{highest.get('settings', {}).get('typography', {}).get('headingScale')})."
    )
