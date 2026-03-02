import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Daisy-chain: Craft heading→Ride, Ride body→Taste, Taste button→Sense. Sense scales=100."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])

    craft = next((t for t in themes if t.get("name") == "Craft"), None)
    ride = next((t for t in themes if t.get("name") == "Ride"), None)
    taste = next((t for t in themes if t.get("name") == "Taste"), None)
    sense = next((t for t in themes if t.get("name") == "Sense"), None)

    if not all([craft, ride, taste, sense]):
        return False, "One or more themes not found."

    # Seed values: Craft heading=Playfair Display, Ride body=Inter, Taste button=Poppins
    # After copy: Ride heading=Playfair Display, Taste body=Inter, Sense button=Poppins

    ride_typo = ride.get("settings", {}).get("typography", {})
    if ride_typo.get("headingFont") != "Playfair Display":
        return False, (f"Expected Ride heading 'Playfair Display' (from Craft), "
                      f"got '{ride_typo.get('headingFont')}'.")

    taste_typo = taste.get("settings", {}).get("typography", {})
    if taste_typo.get("bodyFont") != "Inter":
        return False, (f"Expected Taste body 'Inter' (from Ride), "
                      f"got '{taste_typo.get('bodyFont')}'.")

    sense_typo = sense.get("settings", {}).get("typography", {})
    if sense_typo.get("buttonFont") != "Poppins":
        return False, (f"Expected Sense button 'Poppins' (from Taste), "
                      f"got '{sense_typo.get('buttonFont')}'.")

    if sense_typo.get("headingScale") != 100:
        return False, f"Expected Sense heading scale 100, got {sense_typo.get('headingScale')}."
    if sense_typo.get("bodyScale") != 100:
        return False, f"Expected Sense body scale 100, got {sense_typo.get('bodyScale')}."

    return True, ("Font chain applied: Craft heading→Ride (Playfair Display), "
                  "Ride body→Taste (Inter), Taste button→Sense (Poppins). "
                  "Sense scales: 100%/100%.")
