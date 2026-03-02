import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that a template for Levothyroxine 50mcg was created with correct defaults."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    rx_templates = state.get("rxTemplates", [])

    # Seed has 12 templates; should now be 13
    if len(rx_templates) < 13:
        return False, (
            f"Expected at least 13 templates (seed had 12, should have added 1). "
            f"Found {len(rx_templates)} templates."
        )

    # Find Levothyroxine 50mcg template (case-insensitive)
    levo_template = None
    for tpl in rx_templates:
        name = (tpl.get("medicationName") or "").lower()
        if "levothyroxine" in name and "50mcg" in name:
            levo_template = tpl
            break

    if levo_template is None:
        tpl_names = [t.get("medicationName", "") for t in rx_templates]
        return False, (
            f"No template containing 'Levothyroxine' and '50mcg' found. "
            f"Current templates: {tpl_names}"
        )

    # Check qty = 30
    qty = levo_template.get("qty")
    if qty != 30:
        return False, f"Levothyroxine 50mcg template qty is {qty}, expected 30"

    # Check refills = 5
    refills = levo_template.get("refills")
    if refills != 5:
        return False, f"Levothyroxine 50mcg template refills is {refills}, expected 5"

    # Check daysSupply = 30
    days_supply = levo_template.get("daysSupply")
    if days_supply != 30:
        return False, f"Levothyroxine 50mcg template daysSupply is {days_supply}, expected 30"

    # Check sig mentions empty stomach
    sig = (levo_template.get("sig") or "").lower()
    empty_stomach_keywords = ["empty stomach", "before breakfast", "before eating", "before food"]
    has_empty_stomach = any(kw in sig for kw in empty_stomach_keywords)
    if not has_empty_stomach:
        return False, (
            f"Levothyroxine 50mcg template sig does not mention empty stomach. "
            f"sig='{levo_template.get('sig')}'"
        )

    return True, (
        f"Levothyroxine 50mcg template created successfully. "
        f"qty={qty}, refills={refills}, daysSupply={days_supply}, "
        f"sig='{levo_template.get('sig')}', total templates={len(rx_templates)}"
    )
