import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Dawn and Craft both: heading=Merriweather, body=Lora, headingScale=115, bodyScale=95."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    dawn = next((t for t in themes if t.get("name") == "Dawn"), None)
    craft = next((t for t in themes if t.get("name") == "Craft"), None)

    if dawn is None:
        return False, "Theme 'Dawn' not found."
    if craft is None:
        return False, "Theme 'Craft' not found."

    expected = {
        "headingFont": "Merriweather",
        "bodyFont": "Lora",
        "headingScale": 115,
        "bodyScale": 95,
    }

    for theme_name, theme in [("Dawn", dawn), ("Craft", craft)]:
        typo = theme.get("settings", {}).get("typography", {})
        for key, val in expected.items():
            actual = typo.get(key)
            if actual != val:
                return False, (f"Expected {theme_name} {key}={val!r}, "
                              f"got {actual!r}.")

    return True, ("Dawn and Craft typography matched: Merriweather/Lora, "
                  "heading scale 115%, body scale 95%.")
