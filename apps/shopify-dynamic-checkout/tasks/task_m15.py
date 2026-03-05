import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found in state."

    settings = dawn.get("settings", {})
    colors = settings.get("colors", {})

    secondary_bg = colors.get("secondaryBg")
    if secondary_bg != "#E5E7EB":
        return (
            False,
            f"Expected Dawn secondaryBg to be '#E5E7EB', but got '{secondary_bg}'.",
        )

    secondary_text = colors.get("secondaryText")
    if secondary_text != "#374151":
        return (
            False,
            f"Expected Dawn secondaryText to be '#374151', but got '{secondary_text}'.",
        )

    return True, "Dawn secondary background is #E5E7EB and secondary text is #374151."
