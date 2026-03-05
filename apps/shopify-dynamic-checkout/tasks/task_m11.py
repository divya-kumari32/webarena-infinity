import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])

    sense = next((t for t in themes if t.get("name") == "Sense"), None)
    if sense is None:
        return False, "Theme 'Sense' not found in state."

    if sense.get("role") != "main":
        return (
            False,
            f"Expected Sense theme role to be 'main' (published), but got '{sense.get('role')}'.",
        )

    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    if dawn is None:
        return False, "Theme 'Dawn' not found in state."

    if dawn.get("role") == "main":
        return False, "Dawn theme still has role 'main'; it should no longer be the live theme."

    settings = sense.get("settings", {})
    typography = settings.get("typography", {})
    body_font = typography.get("bodyFont")
    if body_font != "Roboto":
        return (
            False,
            f"Expected Sense bodyFont to be 'Roboto', but got '{body_font}'.",
        )

    return True, "Sense is published as the live theme and its body font is set to Roboto."
