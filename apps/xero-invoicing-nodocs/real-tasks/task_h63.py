import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Update company phone and email in settings to match Atlas Import/Export Ltd."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    contacts = state.get("contacts", [])
    settings = state.get("settings", {})
    errors = []

    # Find Atlas Import/Export Ltd
    atlas = next(
        (c for c in contacts if c.get("name") == "Atlas Import/Export Ltd"), None
    )
    if atlas is None:
        return False, "Contact 'Atlas Import/Export Ltd' not found"

    atlas_phone = atlas.get("phone", "")
    atlas_email = atlas.get("email", "")

    company_phone = settings.get("companyPhone", "")
    if company_phone != atlas_phone:
        errors.append(
            f"Company phone is '{company_phone}', expected '{atlas_phone}' "
            f"(Atlas Import/Export Ltd's phone)"
        )

    company_email = settings.get("companyEmail", "")
    if company_email != atlas_email:
        errors.append(
            f"Company email is '{company_email}', expected '{atlas_email}' "
            f"(Atlas Import/Export Ltd's email)"
        )

    if errors:
        return False, "; ".join(errors)

    return True, "Company phone and email updated to match Atlas Import/Export Ltd"
