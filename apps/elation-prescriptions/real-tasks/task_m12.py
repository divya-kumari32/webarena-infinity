import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Ibuprofen was added as a drug allergy with stomach upset/GI bleeding, moderate severity."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    current_patient = state.get("currentPatient", {})
    allergies = current_patient.get("allergies", [])

    # Seed has 4 allergies; should now be 5
    if len(allergies) < 5:
        return False, (
            f"Expected at least 5 allergies (seed had 4, should have added 1). "
            f"Found {len(allergies)} allergies."
        )

    # Find Ibuprofen allergy (case-insensitive)
    ibuprofen_allergy = None
    for allergy in allergies:
        allergen = (allergy.get("allergen") or "").lower()
        if "ibuprofen" in allergen:
            ibuprofen_allergy = allergy
            break

    if ibuprofen_allergy is None:
        allergen_names = [a.get("allergen", "") for a in allergies]
        return False, (
            f"No allergy with allergen containing 'Ibuprofen' found. "
            f"Current allergens: {allergen_names}"
        )

    # Check type = drug
    allergy_type = (ibuprofen_allergy.get("type") or "").lower()
    if allergy_type != "drug":
        return False, f"Ibuprofen allergy type is '{ibuprofen_allergy.get('type')}', expected 'drug'"

    # Check severity = Moderate (case-insensitive)
    severity = (ibuprofen_allergy.get("severity") or "").lower()
    if severity != "moderate":
        return False, f"Ibuprofen allergy severity is '{ibuprofen_allergy.get('severity')}', expected 'Moderate'"

    # Check reaction mentions stomach or GI
    reaction = (ibuprofen_allergy.get("reaction") or "").lower()
    gi_keywords = ["stomach", "gi", "gastrointestinal", "bleeding", "gastric"]
    has_gi = any(kw in reaction for kw in gi_keywords)
    if not has_gi:
        return False, (
            f"Ibuprofen allergy reaction does not mention stomach/GI issues. "
            f"reaction='{ibuprofen_allergy.get('reaction')}'"
        )

    return True, (
        f"Ibuprofen drug allergy added successfully. "
        f"severity='{ibuprofen_allergy.get('severity')}', "
        f"type='{ibuprofen_allergy.get('type')}', "
        f"reaction='{ibuprofen_allergy.get('reaction')}', "
        f"total allergies={len(allergies)}"
    )
