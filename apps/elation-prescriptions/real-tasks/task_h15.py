import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that bee stings was added as a severe environmental allergy."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    current_patient = state.get("currentPatient", {})
    allergies = current_patient.get("allergies", [])

    # Find bee allergy (case-insensitive)
    bee_allergy = None
    for allergy in allergies:
        allergen = (allergy.get("allergen") or "").lower()
        if "bee" in allergen:
            bee_allergy = allergy
            break

    if bee_allergy is None:
        allergen_names = [a.get("allergen", "") for a in allergies]
        return False, (
            f"No allergy containing 'bee' found in currentPatient.allergies. "
            f"Current allergens: {allergen_names}"
        )

    # Check severity is Severe (case-insensitive)
    severity = (bee_allergy.get("severity") or "").lower()
    if severity != "severe":
        return False, (
            f"Bee allergy severity is '{bee_allergy.get('severity')}', expected 'Severe'."
        )

    # Check type is environmental (case-insensitive)
    allergy_type = (bee_allergy.get("type") or "").lower()
    if allergy_type != "environmental":
        return False, (
            f"Bee allergy type is '{bee_allergy.get('type')}', expected 'environmental'."
        )

    # Check reaction mentions swelling or anaphylaxis (case-insensitive)
    reaction = (bee_allergy.get("reaction") or "").lower()
    reaction_keywords = ["swelling", "anaphylaxis", "anaphylactic"]
    has_reaction = any(kw in reaction for kw in reaction_keywords)
    if not has_reaction:
        return False, (
            f"Bee allergy reaction does not mention 'swelling' or 'anaphylaxis'. "
            f"reaction='{bee_allergy.get('reaction')}'"
        )

    # Verify count increased from seed (4 -> 5)
    if len(allergies) < 5:
        return False, (
            f"Expected at least 5 allergies after adding bee stings "
            f"(seed had 4), but found {len(allergies)}."
        )

    return True, (
        f"Bee sting allergy added successfully. "
        f"allergen='{bee_allergy.get('allergen')}', severity='{bee_allergy.get('severity')}', "
        f"type='{bee_allergy.get('type')}', reaction='{bee_allergy.get('reaction')}', "
        f"total allergies: {len(allergies)}."
    )
