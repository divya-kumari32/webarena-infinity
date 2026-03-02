import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Cyclobenzaprine 10mg was prescribed as a temporary med, qty 30."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    errors = []

    # Find Cyclobenzaprine 10mg in temporaryMeds
    temporary_meds = state.get("temporaryMeds", [])
    cyclo_match = [
        m for m in temporary_meds
        if "cyclobenzaprine" in m.get("medicationName", "").lower()
        and "10mg" in m.get("medicationName", "").lower()
    ]

    if not cyclo_match:
        return False, (
            "No medication found in temporaryMeds containing 'Cyclobenzaprine' and '10mg'. "
            f"temporaryMeds count: {len(temporary_meds)}"
        )

    med = cyclo_match[0]

    # Check classification is temporary
    classification = med.get("classification")
    if classification != "temporary":
        errors.append(
            f"classification is '{classification}', expected 'temporary'"
        )

    # Check qty is 30
    qty = med.get("qty")
    if qty != 30:
        errors.append(f"qty is {qty}, expected 30")

    # Check sig mentions three times daily, TID, or similar frequency
    sig = med.get("sig", "").lower()
    has_frequency = (
        "three times daily" in sig
        or "tid" in sig
        or "3 times daily" in sig
        or "three times a day" in sig
        or "3 times a day" in sig
    )
    if not has_frequency:
        errors.append(
            f"sig is '{med.get('sig', '')}', expected it to mention 'three times daily', 'TID', or similar"
        )

    # Seed has 3 temp meds, should now have 4
    if len(temporary_meds) != 4:
        errors.append(
            f"Expected 4 temporaryMeds after adding Cyclobenzaprine (seed had 3), "
            f"found {len(temporary_meds)}"
        )

    if errors:
        return False, f"Cyclobenzaprine prescription issues: {'; '.join(errors)}"

    return True, (
        f"Cyclobenzaprine 10mg successfully prescribed as temporary med. "
        f"classification='temporary', qty=30, sig='{med.get('sig', '')}', "
        f"temporaryMeds count=4."
    )
