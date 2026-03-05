import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Deactivate two apps with same conflict reason, activate inactive non-conflicting app, activate Amazon Pay."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("installedApps", [])
    payment_methods = state.get("paymentMethods", [])

    # The two apps sharing "Apps that interact with the cart..." reason:
    # CartHook Post Purchase Offers and ReConvert Upsell & Cross Sell
    carthook = next((a for a in apps if "CartHook" in a.get("name", "")), None)
    reconvert = next((a for a in apps if "ReConvert" in a.get("name", "")), None)

    if carthook is None:
        return False, "CartHook app not found."
    if reconvert is None:
        return False, "ReConvert app not found."

    if carthook.get("isActive") is not False:
        return False, (f"Expected CartHook deactivated (shares conflict reason), "
                      f"got isActive={carthook.get('isActive')}.")
    if reconvert.get("isActive") is not False:
        return False, (f"Expected ReConvert deactivated (shares conflict reason), "
                      f"got isActive={reconvert.get('isActive')}.")

    # The non-conflicting inactive app in seed: Privy Pop Ups & Email
    privy = next((a for a in apps if "Privy" in a.get("name", "")), None)
    if privy is None:
        return False, "Privy app not found."
    if privy.get("isActive") is not True:
        return False, f"Expected Privy activated, got isActive={privy.get('isActive')}."

    # Check Amazon Pay is active
    amazon = next((m for m in payment_methods if m.get("name") == "Amazon Pay"), None)
    if amazon is None:
        return False, "Amazon Pay not found."
    if amazon.get("isActive") is not True:
        return False, f"Expected Amazon Pay active, got isActive={amazon.get('isActive')}."

    return True, ("CartHook and ReConvert deactivated (same conflict reason). "
                  "Privy activated. Amazon Pay active.")
