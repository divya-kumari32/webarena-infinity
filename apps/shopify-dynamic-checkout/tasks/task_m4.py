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

    accent_bg = colors.get("accentButtonBg")
    if accent_bg != "#2563EB":
        return (
            False,
            f"Expected Dawn accentButtonBg to be '#2563EB', but got '{accent_bg}'.",
        )

    accent_text = colors.get("accentButtonText")
    if accent_text != "#FFFFFF":
        return (
            False,
            f"Expected Dawn accentButtonText to be '#FFFFFF', but got '{accent_text}'.",
        )

    return True, "Dawn checkout button is blue (#2563EB) with white text (#FFFFFF)."
