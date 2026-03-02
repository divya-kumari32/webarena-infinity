import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the Latex allergy was removed from the patient's allergies."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    # Get allergies from currentPatient
    current_patient = state.get("currentPatient", {})
    allergies = current_patient.get("allergies", [])

    # Check that no allergy with allergen='Latex' exists
    for allergy in allergies:
        if allergy.get("allergen") == "Latex":
            return False, "Latex allergy still exists in currentPatient.allergies"

    # Verify we didn't lose all allergies (seed had 4, should now have 3)
    if len(allergies) < 3:
        return False, (
            f"Expected at least 3 remaining allergies after removing Latex, "
            f"but found {len(allergies)}. Other allergies may have been accidentally removed."
        )

    return True, (
        f"Latex allergy removed successfully. "
        f"{len(allergies)} allergies remain in currentPatient.allergies."
    )
