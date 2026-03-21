#!/usr/bin/env python3
"""Build a grid GIF showcasing agent interaction trajectories across apps.

For each selected app, picks a random task trajectory, extracts screenshots
(from report.html base64 or local PNGs), creates per-cell GIFs, then tiles
them into a single grid GIF.

For figma-slides (no trajectory data), takes screenshots via Playwright.

Usage:
    python analysis/make_grid_gif.py [--output analysis/output/grid.gif]
"""

import base64
import io
import random
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
S3_RESULTS = REPO / "analysis" / "s3_results"
LOCAL_APPS = REPO / "apps"
OUTPUT_DIR = REPO / "analysis" / "output"

# All available apps for the grid
GRID_APPS = [
    "gmail",
    "gitlab-plan-and-track",
    "xero-invoicing",
    "elation-prescriptions",
    "handshake-career-exploration",
    "superhuman-general",
    "linear-account-settings-v2",
    "paypal-my-wallet",
    "elation-clinical-records",
    "elation-patient-communication",
    "gmail-accounts-and-contacts",
    "figma-text-and-typography",
    "figma-slides",
    "clio-matters",
    "shopify-web-performance",
]

# Display names for labels
DISPLAY_NAMES = {
    "gmail": "Gmail",
    "gitlab-plan-and-track": "GitLab",
    "xero-invoicing": "Xero Invoicing",
    "elation-prescriptions": "Elation Rx",
    "handshake-career-exploration": "Handshake",
    "superhuman-general": "Superhuman",
    "linear-account-settings-v2": "Linear Settings",
    "paypal-my-wallet": "PayPal Wallet",
    "figma-slides": "Figma Slides",
    "elation-patient-communication": "Elation Comms",
    "gmail-accounts-and-contacts": "Gmail Contacts",
    "figma-text-and-typography": "Figma Typography",
    "clio-matters": "Clio Matters",
    "elation-clinical-records": "Elation Clinical",
    "shopify-web-performance": "Shopify Perf",
}

# Target cell size for each GIF in the grid
CELL_W = 360
CELL_H = 225
FRAME_DELAY_MS = 500  # Time per frame in the GIF
LABEL_HEIGHT = 22


def extract_screenshots_from_report(app_name: str) -> list[list[bytes]]:
    """Extract per-task screenshot sequences from the latest report.html.

    Returns list of trajectories, each a list of PNG bytes.
    """
    app_dir = S3_RESULTS / app_name
    if not app_dir.is_dir():
        return []

    reports = list(app_dir.rglob("report.html"))
    if not reports:
        return []

    # Prefer final phase reports (p5 = phase 5 final regression)
    p5_reports = [r for r in reports if "p5" in r.parent.name or "p5" in r.parent.parent.name]
    pool = p5_reports if p5_reports else reports
    latest = max(pool, key=lambda p: p.stat().st_mtime)

    html = latest.read_text()

    # Parse task sections: each task row has <code>task_XX</code> followed by
    # step divs containing screenshots
    task_pattern = re.compile(r"<code>(task_[ehm]?\d+)</code>")
    task_positions = [(m.start(), m.group(1)) for m in task_pattern.finditer(html)]

    trajectories = []
    for idx, (pos, task_id) in enumerate(task_positions):
        # Get HTML chunk for this task (until next task or end)
        end_pos = task_positions[idx + 1][0] if idx + 1 < len(task_positions) else len(html)
        chunk = html[pos:end_pos]

        # Extract all base64 screenshot images from this chunk
        img_pattern = re.compile(r"data:image/png;base64,([A-Za-z0-9+/=]+)")
        images = []
        for m in img_pattern.finditer(chunk):
            try:
                png_bytes = base64.b64decode(m.group(1))
                img = Image.open(io.BytesIO(png_bytes))
                img.verify()
                images.append(png_bytes)
            except Exception:
                continue

        if len(images) >= 2:
            trajectories.append(images)

    return trajectories


def get_local_screenshots(app_name: str) -> list[list[bytes]]:
    """Get trajectories from local apps/*/results/ directories."""
    local_name = app_name
    if app_name == "linear-account-settings-v2":
        local_name = "linear-account-settings"

    results_dir = LOCAL_APPS / local_name / "results"
    if not results_dir.is_dir():
        return []

    trajectories = []
    for run_dir in results_dir.iterdir():
        if not run_dir.is_dir():
            continue
        for task_dir in run_dir.iterdir():
            if not task_dir.is_dir() or not task_dir.name.startswith("task_"):
                continue
            ss_dir = task_dir / "screenshots"
            if not ss_dir.is_dir():
                continue
            steps = sorted(ss_dir.glob("step_*.png"), key=lambda p: int(p.stem.split("_")[1]))
            if len(steps) >= 2:
                trajectories.append([s.read_bytes() for s in steps])

    return trajectories


def take_app_screenshots(port: int, n_screenshots: int = 5) -> list[bytes]:
    """Take screenshots of a running app by interacting via Playwright."""
    script = f"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={{"width": 1440, "height": 900}})

        url = "http://localhost:{port}"
        await page.goto(url, wait_until="load", timeout=15000)
        await page.wait_for_timeout(3000)

        # Take initial screenshot
        ss = await page.screenshot(type="png")
        with open("/tmp/app_ss_{port}_0.png", "wb") as f:
            f.write(ss)

        # Click on various interactive elements to get different views
        shot_idx = 1
        selectors = [
            "nav a, .nav-item, .sidebar-item, .tab, [role='tab']",
            ".menu-item, .list-item, button:not([disabled])",
        ]
        for selector in selectors:
            if shot_idx >= {n_screenshots}:
                break
            items = await page.query_selector_all(selector)
            for item in items[1:6]:  # skip first, try next 5
                if shot_idx >= {n_screenshots}:
                    break
                try:
                    await item.click()
                    await page.wait_for_timeout(800)
                    ss = await page.screenshot(type="png")
                    with open(f"/tmp/app_ss_{port}_{{shot_idx}}.png", "wb") as f:
                        f.write(ss)
                    shot_idx += 1
                except Exception:
                    continue

        await browser.close()

asyncio.run(main())
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        print(f"  Playwright stderr: {result.stderr[:200]}")

    images = []
    for i in range(n_screenshots):
        f = Path(f"/tmp/app_ss_{port}_{i}.png")
        if f.exists():
            images.append(f.read_bytes())
    return images


def take_figma_screenshots(port: int = 9004, n_screenshots: int = 6) -> list[bytes]:
    """Take screenshots of figma-slides by browsing different pages via Playwright."""
    script = f"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={{"width": 1440, "height": 900}})

        url = "http://localhost:{port}"
        await page.goto(url, wait_until="load", timeout=15000)
        await page.wait_for_timeout(3000)

        # Screenshot 1: Main view (slide 1)
        ss = await page.screenshot(type="png")
        with open("/tmp/figma_ss_0.png", "wb") as f:
            f.write(ss)

        # Find sidebar slide items
        sidebar_items = await page.query_selector_all(".slides-panel .slide-item, .slide-list .slide-thumb, .slide-panel .slide, .slide-thumbnail-item")
        print(f"Found {{len(sidebar_items)}} sidebar items")

        if sidebar_items and len(sidebar_items) > 1:
            indices_to_try = [2, 5, 8, 11, 14]
            shot_idx = 1
            for i in indices_to_try:
                if i < len(sidebar_items) and shot_idx < {n_screenshots}:
                    try:
                        await sidebar_items[i].click()
                        await page.wait_for_timeout(800)
                        ss = await page.screenshot(type="png")
                        with open(f"/tmp/figma_ss_{{shot_idx}}.png", "wb") as f:
                            f.write(ss)
                        shot_idx += 1
                    except Exception as e:
                        print(f"Click failed for slide {{i}}: {{e}}")

            if shot_idx < {n_screenshots}:
                try:
                    share_btn = await page.query_selector("button:has-text('Share'), [data-action='share'], .share-button")
                    if share_btn:
                        await share_btn.click()
                        await page.wait_for_timeout(800)
                        ss = await page.screenshot(type="png")
                        with open(f"/tmp/figma_ss_{{shot_idx}}.png", "wb") as f:
                            f.write(ss)
                        shot_idx += 1
                        close = await page.query_selector(".modal-close, .close-button, [data-action='close-modal']")
                        if close:
                            await close.click()
                            await page.wait_for_timeout(500)
                except Exception as e:
                    print(f"Share button: {{e}}")
        else:
            print("No sidebar items found, trying fallback approach")
            for i in range(1, {n_screenshots}):
                await page.wait_for_timeout(500)
                ss = await page.screenshot(type="png")
                with open(f"/tmp/figma_ss_{{i}}.png", "wb") as f:
                    f.write(ss)

        await browser.close()

asyncio.run(main())
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        print(f"Playwright stderr: {result.stderr}")

    images = []
    for i in range(n_screenshots):
        f = Path(f"/tmp/figma_ss_{i}.png")
        if f.exists():
            images.append(f.read_bytes())
    return images


def resize_to_cell(img_bytes: bytes) -> Image.Image:
    """Resize a screenshot PNG to fit inside the grid cell (letterboxed, no crop)."""
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    # Fit inside cell — use min ratio so nothing is cropped
    ratio = min(CELL_W / img.width, CELL_H / img.height)
    new_w = int(img.width * ratio)
    new_h = int(img.height * ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    # Center on dark background
    cell = Image.new("RGB", (CELL_W, CELL_H), (15, 15, 24))
    x_offset = (CELL_W - new_w) // 2
    y_offset = (CELL_H - new_h) // 2
    cell.paste(img, (x_offset, y_offset))
    return cell


def add_label(frame: Image.Image, label: str) -> Image.Image:
    """Add an app name label bar at the bottom of a frame."""
    new_h = frame.height + LABEL_HEIGHT
    labeled = Image.new("RGB", (frame.width, new_h), (20, 20, 30))
    labeled.paste(frame, (0, 0))

    draw = ImageDraw.Draw(labeled)
    draw.rectangle(
        [(0, frame.height), (frame.width, new_h)],
        fill=(25, 25, 40),
    )
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), label, font=font)
    text_w = bbox[2] - bbox[0]
    text_x = (frame.width - text_w) // 2
    text_y = frame.height + (LABEL_HEIGHT - (bbox[3] - bbox[1])) // 2
    draw.text((text_x, text_y), label, fill=(200, 200, 220), font=font)

    return labeled


def make_cell_frames(screenshots: list[bytes], label: str) -> list[Image.Image]:
    """Create labeled frames for one grid cell."""
    frames = []
    for ss in screenshots:
        img = resize_to_cell(ss)
        labeled = add_label(img, label)
        frames.append(labeled)
    return frames


def build_grid_gif(
    cells: list[tuple[str, list[bytes]]],
    output_path: Path,
    cols: int = 4,
):
    """Combine multiple cell trajectories into a grid GIF.

    Each cell is (label, [png_bytes, ...]).
    Shorter trajectories loop so every cell always animates.
    """
    max_frames = max(len(screenshots) for _, screenshots in cells)

    cell_frame_sets = []
    for label, screenshots in cells:
        frames = make_cell_frames(screenshots, label)
        n = len(frames)
        # Loop shorter trajectories (cycle through frames, not hold last)
        if n < max_frames:
            looped = []
            for i in range(max_frames):
                looped.append(frames[i % n])
            frames = looped
        cell_frame_sets.append(frames)

    rows = (len(cells) + cols - 1) // cols
    cell_total_h = CELL_H + LABEL_HEIGHT
    gap = 3
    grid_w = cols * CELL_W + (cols - 1) * gap
    grid_h = rows * cell_total_h + (rows - 1) * gap

    grid_frames = []
    for frame_idx in range(max_frames):
        grid = Image.new("RGB", (grid_w, grid_h), (15, 15, 24))
        for cell_idx, frames in enumerate(cell_frame_sets):
            row = cell_idx // cols
            col = cell_idx % cols
            x = col * (CELL_W + gap)
            y = row * (cell_total_h + gap)
            grid.paste(frames[frame_idx], (x, y))
        grid_frames.append(grid)

    # Save as GIF
    output_path.parent.mkdir(parents=True, exist_ok=True)
    grid_frames[0].save(
        output_path,
        save_all=True,
        append_images=grid_frames[1:],
        duration=FRAME_DELAY_MS,
        loop=0,
        optimize=True,
    )
    print(f"Saved grid GIF: {output_path} ({grid_w}x{grid_h}, {max_frames} frames, {len(cells)} cells)")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Build grid GIF of agent trajectories")
    parser.add_argument("--output", type=str, default=str(OUTPUT_DIR / "trajectory_grid.gif"))
    parser.add_argument("--cols", type=int, default=4, help="Number of columns in grid")
    parser.add_argument("--include-figma", action="store_true", help="Include Figma Slides screenshots via Playwright")
    parser.add_argument("--figma-port", type=int, default=9004)
    parser.add_argument("--seed", type=int, default=42, help="Random seed for trajectory selection")
    args = parser.parse_args()

    random.seed(args.seed)
    output = Path(args.output)

    cells = []  # list of (label, [png_bytes, ...])

    for app_name in GRID_APPS:
        print(f"\nProcessing {app_name}...")
        label = DISPLAY_NAMES.get(app_name, app_name)

        # Try local screenshots first, then report.html
        trajectories = get_local_screenshots(app_name)
        if not trajectories:
            trajectories = extract_screenshots_from_report(app_name)

        if not trajectories:
            print(f"  No trajectories found for {app_name}, skipping")
            continue

        # Pick a random trajectory with good length (3-8 steps)
        good = [t for t in trajectories if 3 <= len(t) <= 8]
        if not good:
            good = [t for t in trajectories if len(t) >= 2]
        if not good:
            print(f"  No suitable trajectories for {app_name}, skipping")
            continue

        chosen = random.choice(good)
        # Cap trajectory at 8 frames max to keep GIF manageable
        if len(chosen) > 8:
            chosen = chosen[:8]
        print(f"  Selected trajectory with {len(chosen)} frames")
        cells.append((label, chosen))

    # Figma slides via Playwright (browsing, not trajectory)
    if args.include_figma:
        # Remove figma-slides from cells if it was added from s3_results
        # (replace with Playwright-captured screenshots)
        cells = [(l, s) for l, s in cells if l != DISPLAY_NAMES["figma-slides"]]
        print(f"\nTaking Figma Slides screenshots (port {args.figma_port})...")
        figma_shots = take_figma_screenshots(port=args.figma_port)
        if figma_shots:
            print(f"  Got {len(figma_shots)} screenshots")
            cells.append((DISPLAY_NAMES["figma-slides"], figma_shots))
        else:
            print("  Failed to capture Figma Slides screenshots")

    # Fill remaining slots via Playwright if we need to reach a full grid
    target_cells = args.cols * ((len(cells) + args.cols - 1) // args.cols)
    # Ablation apps (for filling extra slots with distinct content)
    FILL_APPS = [
        ("xero-invoicing-nodocs", 9018, "Xero (Ablation)"),
        ("gmail-accounts-and-contacts-nodocs", 9017, "Gmail Contacts (Abl.)"),
        ("gitlab-plan-and-track-nodocs", 9016, "GitLab (Ablation)"),
        ("figma-slides-nodocs", 9015, "Figma (Ablation)"),
        ("elation-prescriptions-nodocs", 9014, "Elation Rx (Abl.)"),
    ]
    if len(cells) < target_cells:
        for app_name, port, label in FILL_APPS:
            if len(cells) >= target_cells:
                break
            print(f"\nFilling slot: taking screenshots of {app_name} (port {port})...")
            shots = take_app_screenshots(port=port, n_screenshots=5)
            if len(shots) >= 2:
                print(f"  Got {len(shots)} screenshots")
                cells.append((label, shots))
            else:
                print(f"  Not enough screenshots for {app_name}")

    if not cells:
        print("No cells to build grid from!")
        sys.exit(1)

    print(f"\nBuilding grid GIF with {len(cells)} cells, {args.cols} columns...")
    build_grid_gif(cells, output, cols=args.cols)


if __name__ == "__main__":
    main()
