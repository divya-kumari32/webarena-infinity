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

    primary_bg = colors.get("primaryBg")
    if primary_bg != "#F0F0F0":
        return (
            False,
            f"Expected Dawn primaryBg to be '#F0F0F0', but got '{primary_bg}'.",
        )

    primary_text = colors.get("primaryText")
    if primary_text != "#333333":
        return (
            False,
            f"Expected Dawn primaryText to be '#333333', but got '{primary_text}'.",
        )

    return True, "Dawn primary background is #F0F0F0 and primary text is #333333."
