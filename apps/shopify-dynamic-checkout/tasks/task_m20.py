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
    dawn_id = dawn.get("id")

    templates = state.get("templates", [])
    default_tmpl = next(
        (t for t in templates if t.get("themeId") == dawn_id and t.get("name") == "Default product"),
        None,
    )
    if default_tmpl is None:
        return False, f"Template 'Default product' not found for Dawn theme (id={dawn_id})."

    buy_button_text = default_tmpl.get("buyButtonText")
    if buy_button_text != "Buy now":
        return (
            False,
            f"Expected Dawn default template buyButtonText to be 'Buy now', "
            f"but got '{buy_button_text}'.",
        )

    return True, "Dawn default template buy button text is 'Buy now'."
