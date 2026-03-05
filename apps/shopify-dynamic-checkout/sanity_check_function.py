#!/usr/bin/env python3
"""
Sanity check for Shopify Dynamic Checkout function-test tasks.

For each task, directly applies the expected end-state (bypassing the agent),
then runs the verifier and asserts it passes.

Usage:
    python3 sanity_check_function.py                     # All tasks, sequential
    python3 sanity_check_function.py --workers N          # N parallel environments
    python3 sanity_check_function.py --task-id task_5     # Single task
    python3 sanity_check_function.py --port 9000          # Custom base port
"""
import argparse
import importlib.util
import json
import os
import socket
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

APP_DIR = Path(__file__).resolve().parent
TASKS_FILE = APP_DIR / "function-tasks.json"

# JS snippet to evaluate data.js and emit the seed state as JSON
_SEED_STATE_JS = """
const fs = require('fs');
const vm = require('vm');
const code = fs.readFileSync(process.argv[1], 'utf8');
vm.runInThisContext(code);

const state = {
    currentUser: JSON.parse(JSON.stringify(CURRENT_USER)),
    themes: JSON.parse(JSON.stringify(THEMES)),
    templates: JSON.parse(JSON.stringify(TEMPLATES)),
    themePages: JSON.parse(JSON.stringify(THEME_PAGES)),
    themeSections: JSON.parse(JSON.stringify(THEME_SECTIONS)),
    paymentMethods: JSON.parse(JSON.stringify(PAYMENT_METHODS)),
    shopPromise: JSON.parse(JSON.stringify(SHOP_PROMISE)),
    products: JSON.parse(JSON.stringify(PRODUCTS)),
    collections: JSON.parse(JSON.stringify(COLLECTIONS)),
    installedApps: JSON.parse(JSON.stringify(INSTALLED_APPS)),
    cartAttributes: JSON.parse(JSON.stringify(CART_ATTRIBUTES)),
    activityLog: JSON.parse(JSON.stringify(ACTIVITY_LOG)),
    availableFonts: JSON.parse(JSON.stringify(AVAILABLE_FONTS)),
    _nextThemeId: INITIAL_NEXT_IDS._nextThemeId,
    _nextTemplateId: INITIAL_NEXT_IDS._nextTemplateId,
    _nextSectionId: INITIAL_NEXT_IDS._nextSectionId,
    _nextProductId: INITIAL_NEXT_IDS._nextProductId,
    _nextAppId: INITIAL_NEXT_IDS._nextAppId,
    _nextLogId: INITIAL_NEXT_IDS._nextLogId,
    _nextCartAttrId: INITIAL_NEXT_IDS._nextCartAttrId,
    _nextCollectionId: INITIAL_NEXT_IDS._nextCollectionId,
    _seedVersion: SEED_DATA_VERSION
};
process.stdout.write(JSON.stringify(state));
"""


# ---- Helpers ----

def find_entity(entities, **kwargs):
    """Find an entity by attribute match. Raises if not found."""
    for e in entities:
        if all(e.get(k) == v for k, v in kwargs.items()):
            return e
    raise ValueError(f"Entity not found: {kwargs}")


def find_theme(state, name):
    return find_entity(state["themes"], name=name)


def find_template(state, theme_name, template_name):
    theme = find_theme(state, theme_name)
    return find_entity(state["templates"], themeId=theme["id"], name=template_name)


def find_default_template(state, theme_name):
    theme = find_theme(state, theme_name)
    return find_entity(state["templates"], themeId=theme["id"], isDefault=True)


def find_product(state, title):
    """Find product by title (supports partial match for em dashes)."""
    for p in state["products"]:
        if p["title"] == title or title in p.get("title", ""):
            return p
    raise ValueError(f"Product not found: {title!r}")


def find_payment_method(state, name):
    return find_entity(state["paymentMethods"], name=name)


def find_app(state, name):
    """Find app by name (supports partial match)."""
    for a in state["installedApps"]:
        if a["name"] == name or name in a.get("name", ""):
            return a
    raise ValueError(f"App not found: {name!r}")


def find_cart_attr(state, name):
    return find_entity(state["cartAttributes"], name=name)


def find_section(state, theme_name, page_type, section_type):
    theme = find_theme(state, theme_name)
    page = find_entity(state["themePages"], themeId=theme["id"], type=page_type)
    return find_entity(state["themeSections"], pageId=page["id"], type=section_type)


# ---- Solve Functions ----

def solve_task_1(state):
    """Publish the Craft theme."""
    for t in state["themes"]:
        if t["role"] == "main":
            t["role"] = "unpublished"
    craft = find_theme(state, "Craft")
    craft["role"] = "main"


def solve_task_2(state):
    """Disable accelerated checkout on Dawn's Default product template."""
    tmpl = find_template(state, "Dawn", "Default product")
    tmpl["showAcceleratedCheckout"] = False


def solve_task_3(state):
    """Enable accelerated checkout on Craft's Default product template."""
    tmpl = find_template(state, "Craft", "Default product")
    tmpl["showAcceleratedCheckout"] = True


def solve_task_4(state):
    """Activate Amazon Pay."""
    pm = find_payment_method(state, "Amazon Pay")
    pm["isActive"] = True


def solve_task_5(state):
    """Deactivate Shop Pay."""
    pm = find_payment_method(state, "Shop Pay")
    pm["isActive"] = False


def solve_task_6(state):
    """Enable Shop Promise."""
    state["shopPromise"]["isActive"] = True
    state["shopPromise"]["prioritizesShopPay"] = True


def solve_task_7(state):
    """Disable Gift wrapping cart attribute."""
    attr = find_cart_attr(state, "Gift wrapping")
    attr["isActive"] = False


def solve_task_8(state):
    """Enable Terms and conditions cart attribute."""
    attr = find_cart_attr(state, "Terms and conditions")
    attr["isActive"] = True


def solve_task_9(state):
    """Deactivate Currency Converter Plus app."""
    app = find_app(state, "Currency Converter Plus")
    app["isActive"] = False


def solve_task_10(state):
    """Activate CartHook Post Purchase Offers app."""
    app = find_app(state, "CartHook")
    app["isActive"] = True


def solve_task_11(state):
    """Change Cashmere Beanie status to active."""
    product = find_product(state, "Cashmere Beanie")
    product["status"] = "active"


def solve_task_12(state):
    """Change Classic Cotton T-Shirt status to draft."""
    product = find_product(state, "Classic Cotton T-Shirt")
    product["status"] = "draft"


def solve_task_13(state):
    """Assign Leather Crossbody Bag to Default product template."""
    tmpl = find_template(state, "Dawn", "Default product")
    product = find_product(state, "Leather Crossbody Bag")
    product["templateId"] = tmpl["id"]


def solve_task_14(state):
    """Assign Canvas Sneakers to Product - No checkout buttons template."""
    tmpl = find_template(state, "Dawn", "Product - No checkout buttons")
    product = find_product(state, "Canvas Sneakers")
    product["templateId"] = tmpl["id"]


def solve_task_15(state):
    """Create alternate template 'Product - Premium' on Dawn."""
    theme = find_theme(state, "Dawn")
    tmpl_id = "tmpl_" + str(state["_nextTemplateId"])
    state["_nextTemplateId"] += 1
    state["templates"].append({
        "id": tmpl_id,
        "themeId": theme["id"],
        "name": "Product - Premium",
        "handle": "product.product---premium",
        "isDefault": False,
        "isAlternate": True,
        "showAcceleratedCheckout": False,
        "showQuantitySelector": True,
        "buyButtonText": "Add to cart",
        "createdAt": "2026-03-02T12:00:00Z"
    })


def solve_task_16(state):
    """Delete Product - Gift cards template from Dawn."""
    theme = find_theme(state, "Dawn")
    tmpl = find_template(state, "Dawn", "Product - Gift cards")
    default_tmpl = find_default_template(state, "Dawn")
    # Reassign products
    for p in state["products"]:
        if p["templateId"] == tmpl["id"]:
            p["templateId"] = default_tmpl["id"]
    state["templates"] = [t for t in state["templates"] if t["id"] != tmpl["id"]]


def solve_task_17(state):
    """Change Dawn's accent button background to #FF5733."""
    theme = find_theme(state, "Dawn")
    theme["settings"]["colors"]["accentButtonBg"] = "#FF5733"


def solve_task_18(state):
    """Change Dawn's primaryBg to #F0F0F0 and primaryText to #333333."""
    theme = find_theme(state, "Dawn")
    theme["settings"]["colors"]["primaryBg"] = "#F0F0F0"
    theme["settings"]["colors"]["primaryText"] = "#333333"


def solve_task_19(state):
    """Change Dawn's heading font to Playfair Display."""
    theme = find_theme(state, "Dawn")
    theme["settings"]["typography"]["headingFont"] = "Playfair Display"


def solve_task_20(state):
    """Change Dawn's body and button font to Roboto."""
    theme = find_theme(state, "Dawn")
    theme["settings"]["typography"]["bodyFont"] = "Roboto"
    theme["settings"]["typography"]["buttonFont"] = "Roboto"


def solve_task_21(state):
    """Set Dawn's heading scale to 120 and body scale to 90."""
    theme = find_theme(state, "Dawn")
    theme["settings"]["typography"]["headingScale"] = 120
    theme["settings"]["typography"]["bodyScale"] = 90


def solve_task_22(state):
    """Disable quantity selector on Dawn's Default product template."""
    tmpl = find_template(state, "Dawn", "Default product")
    tmpl["showQuantitySelector"] = False


def solve_task_23(state):
    """Disable accelerated checkout on Dawn's Home page featured product section."""
    sec = find_section(state, "Dawn", "home", "featured_product")
    sec["showAcceleratedCheckout"] = False


def solve_task_24(state):
    """Deactivate PayPal and Google Pay."""
    find_payment_method(state, "PayPal")["isActive"] = False
    find_payment_method(state, "Google Pay")["isActive"] = False


def solve_task_25(state):
    """Activate Venmo."""
    find_payment_method(state, "Venmo")["isActive"] = True


def solve_task_26(state):
    """Publish Sense theme."""
    for t in state["themes"]:
        if t["role"] == "main":
            t["role"] = "unpublished"
    find_theme(state, "Sense")["role"] = "main"


def solve_task_27(state):
    """Change Heavyweight Hoodie status to active."""
    product = find_product(state, "Heavyweight Hoodie")
    product["status"] = "active"


def solve_task_28(state):
    """Archive Hand-Poured Soy Candle Set."""
    product = find_product(state, "Hand-Poured Soy Candle Set")
    product["status"] = "archived"


def solve_task_29(state):
    """Enable accelerated checkout on both Craft templates."""
    find_template(state, "Craft", "Default product")["showAcceleratedCheckout"] = True
    find_template(state, "Craft", "Product - Featured")["showAcceleratedCheckout"] = True


def solve_task_30(state):
    """Create alternate template 'Product - Express Checkout' on Craft."""
    theme = find_theme(state, "Craft")
    tmpl_id = "tmpl_" + str(state["_nextTemplateId"])
    state["_nextTemplateId"] += 1
    state["templates"].append({
        "id": tmpl_id,
        "themeId": theme["id"],
        "name": "Product - Express Checkout",
        "handle": "product.product---express-checkout",
        "isDefault": False,
        "isAlternate": True,
        "showAcceleratedCheckout": False,
        "showQuantitySelector": True,
        "buyButtonText": "Add to cart",
        "createdAt": "2026-03-02T12:00:00Z"
    })


def solve_task_31(state):
    """Disable Delivery date cart attribute."""
    find_cart_attr(state, "Delivery date")["isActive"] = False


def solve_task_32(state):
    """Deactivate Oberlo Dropshipping app."""
    find_app(state, "Oberlo Dropshipping")["isActive"] = False


def solve_task_33(state):
    """Deactivate ReConvert Upsell & Cross Sell app."""
    find_app(state, "ReConvert Upsell & Cross Sell")["isActive"] = False


def solve_task_34(state):
    """Change Dawn's accent color to #E11D48."""
    find_theme(state, "Dawn")["settings"]["colors"]["accentColor"] = "#E11D48"


def solve_task_35(state):
    """Change Dawn's secondaryBg to #E5E7EB and secondaryText to #374151."""
    colors = find_theme(state, "Dawn")["settings"]["colors"]
    colors["secondaryBg"] = "#E5E7EB"
    colors["secondaryText"] = "#374151"


def solve_task_36(state):
    """Change Dawn's accent button text color to #000000."""
    find_theme(state, "Dawn")["settings"]["colors"]["accentButtonText"] = "#000000"


def solve_task_37(state):
    """Assign Digital Gift Card to Product - No checkout buttons template."""
    tmpl = find_template(state, "Dawn", "Product - No checkout buttons")
    product = find_product(state, "Digital Gift Card")
    product["templateId"] = tmpl["id"]


def solve_task_38(state):
    """Set Dawn's body font to Merriweather and heading font to DM Serif Display."""
    typo = find_theme(state, "Dawn")["settings"]["typography"]
    typo["bodyFont"] = "Merriweather"
    typo["headingFont"] = "DM Serif Display"


def solve_task_39(state):
    """Deactivate all 4 active accelerated payment methods."""
    for name in ["Shop Pay", "Apple Pay", "Google Pay", "PayPal"]:
        find_payment_method(state, name)["isActive"] = False


def solve_task_40(state):
    """Activate Privy Pop Ups & Email app."""
    find_app(state, "Privy Pop Ups & Email")["isActive"] = True


def solve_task_41(state):
    """Publish Ride theme."""
    for t in state["themes"]:
        if t["role"] == "main":
            t["role"] = "unpublished"
    find_theme(state, "Ride")["role"] = "main"


def solve_task_42(state):
    """Delete Product - No checkout buttons from Dawn."""
    tmpl = find_template(state, "Dawn", "Product - No checkout buttons")
    default_tmpl = find_default_template(state, "Dawn")
    for p in state["products"]:
        if p["templateId"] == tmpl["id"]:
            p["templateId"] = default_tmpl["id"]
    state["templates"] = [t for t in state["templates"] if t["id"] != tmpl["id"]]


def solve_task_43(state):
    """Create 'Product - Limited Edition' on Dawn and enable accelerated checkout."""
    theme = find_theme(state, "Dawn")
    tmpl_id = "tmpl_" + str(state["_nextTemplateId"])
    state["_nextTemplateId"] += 1
    state["templates"].append({
        "id": tmpl_id,
        "themeId": theme["id"],
        "name": "Product - Limited Edition",
        "handle": "product.product---limited-edition",
        "isDefault": False,
        "isAlternate": True,
        "showAcceleratedCheckout": True,
        "showQuantitySelector": True,
        "buyButtonText": "Add to cart",
        "createdAt": "2026-03-02T12:00:00Z"
    })


def solve_task_44(state):
    """Assign Titanium Watch to Dawn's Product - Gift cards template."""
    tmpl = find_template(state, "Dawn", "Product - Gift cards")
    product = find_product(state, "Titanium Watch")
    product["templateId"] = tmpl["id"]


def solve_task_45(state):
    """Deactivate Apple Pay."""
    find_payment_method(state, "Apple Pay")["isActive"] = False


def solve_task_46(state):
    """Change Merino Wool Sweater to archived."""
    find_product(state, "Merino Wool Sweater")["status"] = "archived"


def solve_task_47(state):
    """Enable quantity selector on Dawn's Product - Gift cards template."""
    find_template(state, "Dawn", "Product - Gift cards")["showQuantitySelector"] = True


def solve_task_48(state):
    """Disable both Gift wrapping and Delivery date cart attributes."""
    find_cart_attr(state, "Gift wrapping")["isActive"] = False
    find_cart_attr(state, "Delivery date")["isActive"] = False


def solve_task_49(state):
    """Deactivate Currency Converter Plus and ReConvert apps."""
    find_app(state, "Currency Converter Plus")["isActive"] = False
    find_app(state, "ReConvert Upsell & Cross Sell")["isActive"] = False


def solve_task_50(state):
    """Change all three fonts to Montserrat."""
    typo = find_theme(state, "Dawn")["settings"]["typography"]
    typo["headingFont"] = "Montserrat"
    typo["bodyFont"] = "Montserrat"
    typo["buttonFont"] = "Montserrat"


def solve_task_51(state):
    """Change Dawn's accentButtonBg to #2563EB and accentButtonText to #FFFFFF."""
    colors = find_theme(state, "Dawn")["settings"]["colors"]
    colors["accentButtonBg"] = "#2563EB"
    colors["accentButtonText"] = "#FFFFFF"


def solve_task_52(state):
    """Enable Terms & conditions and disable Gift wrapping."""
    find_cart_attr(state, "Terms and conditions")["isActive"] = True
    find_cart_attr(state, "Gift wrapping")["isActive"] = False


def solve_task_53(state):
    """Enable accelerated checkout on Craft's Default product and publish Craft."""
    find_template(state, "Craft", "Default product")["showAcceleratedCheckout"] = True
    for t in state["themes"]:
        if t["role"] == "main":
            t["role"] = "unpublished"
    find_theme(state, "Craft")["role"] = "main"


def solve_task_54(state):
    """Assign Silk Blend Scarf to Dawn's Default product template."""
    tmpl = find_template(state, "Dawn", "Default product")
    product = find_product(state, "Silk Blend Scarf")
    product["templateId"] = tmpl["id"]


def solve_task_55(state):
    """Activate both Amazon Pay and Venmo."""
    find_payment_method(state, "Amazon Pay")["isActive"] = True
    find_payment_method(state, "Venmo")["isActive"] = True


# ---- Solver registry ----

SOLVERS = {
    "task_1": solve_task_1,
    "task_2": solve_task_2,
    "task_3": solve_task_3,
    "task_4": solve_task_4,
    "task_5": solve_task_5,
    "task_6": solve_task_6,
    "task_7": solve_task_7,
    "task_8": solve_task_8,
    "task_9": solve_task_9,
    "task_10": solve_task_10,
    "task_11": solve_task_11,
    "task_12": solve_task_12,
    "task_13": solve_task_13,
    "task_14": solve_task_14,
    "task_15": solve_task_15,
    "task_16": solve_task_16,
    "task_17": solve_task_17,
    "task_18": solve_task_18,
    "task_19": solve_task_19,
    "task_20": solve_task_20,
    "task_21": solve_task_21,
    "task_22": solve_task_22,
    "task_23": solve_task_23,
    "task_24": solve_task_24,
    "task_25": solve_task_25,
    "task_26": solve_task_26,
    "task_27": solve_task_27,
    "task_28": solve_task_28,
    "task_29": solve_task_29,
    "task_30": solve_task_30,
    "task_31": solve_task_31,
    "task_32": solve_task_32,
    "task_33": solve_task_33,
    "task_34": solve_task_34,
    "task_35": solve_task_35,
    "task_36": solve_task_36,
    "task_37": solve_task_37,
    "task_38": solve_task_38,
    "task_39": solve_task_39,
    "task_40": solve_task_40,
    "task_41": solve_task_41,
    "task_42": solve_task_42,
    "task_43": solve_task_43,
    "task_44": solve_task_44,
    "task_45": solve_task_45,
    "task_46": solve_task_46,
    "task_47": solve_task_47,
    "task_48": solve_task_48,
    "task_49": solve_task_49,
    "task_50": solve_task_50,
    "task_51": solve_task_51,
    "task_52": solve_task_52,
    "task_53": solve_task_53,
    "task_54": solve_task_54,
    "task_55": solve_task_55,
}


# ---- Server management ----

def generate_seed_state():
    """Use Node.js to evaluate data.js and produce the seed state JSON."""
    data_js = str(APP_DIR / "js" / "data.js")
    result = subprocess.run(
        ["node", "-e", _SEED_STATE_JS, data_js],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to generate seed state:\n{result.stderr}")
    return json.loads(result.stdout)


def seed_server(server_url, seed_state):
    """PUT the seed state to the server to establish the baseline."""
    resp = requests.put(
        f"{server_url}/api/state",
        json=seed_state,
        headers={"Content-Type": "application/json"},
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to seed server: HTTP {resp.status_code}")


def find_free_port(start=9500):
    """Find a free port starting from `start`."""
    port = start
    while port < start + 200:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                port += 1
    raise RuntimeError(f"No free port found in range {start}-{start+200}")


def start_server(port):
    """Start the app server on the given port."""
    proc = subprocess.Popen(
        [sys.executable, "server.py", "--port", str(port)],
        cwd=str(APP_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(30):
        try:
            requests.get(f"http://localhost:{port}/", timeout=1)
            return proc
        except (requests.ConnectionError, requests.Timeout):
            time.sleep(0.2)
    proc.kill()
    raise RuntimeError(f"Server failed to start on port {port}")


def stop_server(proc):
    """Stop the server process."""
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


# ---- Task runner ----

def load_tasks():
    """Load task definitions from function-tasks.json."""
    with open(TASKS_FILE) as f:
        return json.load(f)


def load_verifier(verify_path):
    """Dynamically load a verifier module."""
    full_path = APP_DIR / verify_path
    spec = importlib.util.spec_from_file_location("verifier", str(full_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.verify


def run_single_task(task, server_url, seed_state):
    """Reset → solve → verify for a single task."""
    task_id = task["id"]
    solver = SOLVERS.get(task_id)
    if not solver:
        return task_id, False, f"No solver defined for {task_id}"

    try:
        # 1. Write seed state (reset)
        resp = requests.put(
            f"{server_url}/api/state",
            json=seed_state,
            headers={"Content-Type": "application/json"},
        )
        if resp.status_code != 200:
            return task_id, False, f"Reset failed: HTTP {resp.status_code}"

        time.sleep(0.1)

        # 2. Read seed state back from server
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return task_id, False, f"Could not read state after reset: HTTP {resp.status_code}"
        state = resp.json()

        # 3. Apply the solve function
        solver(state)

        # 4. Write solved state back
        resp = requests.put(
            f"{server_url}/api/state",
            json=state,
            headers={"Content-Type": "application/json"},
        )
        if resp.status_code != 200:
            return task_id, False, f"Could not write state: HTTP {resp.status_code}"

        # 5. Run the verifier
        verify_fn = load_verifier(task["verify"])
        passed, message = verify_fn(server_url)
        return task_id, passed, message

    except Exception as e:
        return task_id, False, f"Exception: {e}"


def run_tasks_sequential(tasks, port, seed_state):
    """Run all tasks sequentially on a single server."""
    proc = start_server(port)
    server_url = f"http://localhost:{port}"
    results = []
    try:
        seed_server(server_url, seed_state)
        for task in tasks:
            result = run_single_task(task, server_url, seed_state)
            results.append(result)
            status = "\033[32m  PASS\033[0m" if result[1] else "\033[31m  FAIL\033[0m"
            print(f"{status}  {result[0]:12s}  {result[2]}")
    finally:
        stop_server(proc)
    return results


def run_tasks_parallel(tasks, workers, base_port, seed_state):
    """Run tasks in parallel across multiple server instances."""
    results = []

    def worker_fn(task, port):
        proc = start_server(port)
        server_url = f"http://localhost:{port}"
        try:
            seed_server(server_url, seed_state)
            return run_single_task(task, server_url, seed_state)
        finally:
            stop_server(proc)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {}
        for i, task in enumerate(tasks):
            port = base_port + i
            future = executor.submit(worker_fn, task, port)
            futures[future] = task["id"]

        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            status = "\033[32m  PASS\033[0m" if result[1] else "\033[31m  FAIL\033[0m"
            print(f"{status}  {result[0]:12s}  {result[2]}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Shopify Dynamic Checkout function-task sanity check")
    parser.add_argument("--task-id", type=str, help="Run a single task by ID")
    parser.add_argument("--workers", type=int, default=1, help="Number of parallel workers")
    parser.add_argument("--port", type=int, default=9500, help="Base port for servers")
    args = parser.parse_args()

    tasks = load_tasks()
    if args.task_id:
        tasks = [t for t in tasks if t["id"] == args.task_id]
        if not tasks:
            print(f"Task '{args.task_id}' not found.")
            sys.exit(1)

    print("Generating seed state from JS data...")
    seed_state = generate_seed_state()
    print(f"Running {len(tasks)} task(s)...\n")

    if args.workers <= 1:
        port = find_free_port(args.port)
        results = run_tasks_sequential(tasks, port, seed_state)
    else:
        results = run_tasks_parallel(tasks, args.workers, args.port, seed_state)

    # Summary
    passed = sum(1 for _, p, _ in results if p)
    total = len(results)
    failed = [tid for tid, p, _ in results if not p]

    print(f"\n{passed}/{total} passed")
    if failed:
        print(f"Failed: {', '.join(failed)}")
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
