#!/usr/bin/env python3
"""Extract all trajectories and save each as an individual GIF.

Saves to analysis/output/trajectories/{app_name}/task_XX_{n_frames}frames.gif
so you can browse and pick the most visually interesting ones.

Usage:
    python analysis/save_all_trajectories.py
"""

import base64
import io
import re
import sys
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parent.parent
S3_RESULTS = REPO / "analysis" / "s3_results"
LOCAL_APPS = REPO / "apps"
OUTPUT_DIR = REPO / "analysis" / "output" / "trajectories"

FRAME_DELAY_MS = 400
# Resize width for individual GIFs (keep readable but not huge)
GIF_W = 720

# All apps to scan
APPS = [
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


def extract_screenshots_from_report(app_name: str) -> dict[str, list[bytes]]:
    """Extract per-task screenshot sequences from report.html files.

    Returns {task_id: [png_bytes, ...]} for all tasks with screenshots.
    """
    app_dir = S3_RESULTS / app_name
    if not app_dir.is_dir():
        return {}

    reports = list(app_dir.rglob("report.html"))
    if not reports:
        return {}

    # Prefer final phase reports (p5), then latest
    p5_reports = [r for r in reports if "p5" in r.parent.name or "p5" in r.parent.parent.name]
    pool = p5_reports if p5_reports else reports
    latest = max(pool, key=lambda p: p.stat().st_mtime)

    html = latest.read_text()

    task_pattern = re.compile(r"<code>(task_[ehm]?\d+)</code>")
    task_positions = [(m.start(), m.group(1)) for m in task_pattern.finditer(html)]

    result = {}
    for idx, (pos, task_id) in enumerate(task_positions):
        end_pos = task_positions[idx + 1][0] if idx + 1 < len(task_positions) else len(html)
        chunk = html[pos:end_pos]

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
            result[task_id] = images

    return result


def get_local_screenshots(app_name: str) -> dict[str, list[bytes]]:
    """Get trajectories from local apps/*/results/ directories."""
    local_name = app_name
    if app_name == "linear-account-settings-v2":
        local_name = "linear-account-settings"

    results_dir = LOCAL_APPS / local_name / "results"
    if not results_dir.is_dir():
        return {}

    result = {}
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
                key = f"{task_dir.name}__{run_dir.name[:30]}"
                result[key] = [s.read_bytes() for s in steps]

    return result


def compute_visual_diversity(images: list[bytes]) -> float:
    """Score how visually diverse a trajectory is (higher = more varied screenshots)."""
    if len(images) < 2:
        return 0.0

    # Compare consecutive frames by pixel difference
    prev = None
    total_diff = 0
    for img_bytes in images:
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB").resize((180, 112))
        if prev is not None:
            # Mean absolute pixel difference
            diff = sum(
                abs(a - b)
                for pa, pb in zip(prev.getdata(), img.getdata())
                for a, b in zip(pa, pb)
            )
            n_pixels = img.width * img.height * 3
            total_diff += diff / n_pixels
        prev = img

    return total_diff / (len(images) - 1)


def resize_for_gif(img_bytes: bytes) -> Image.Image:
    """Resize screenshot to GIF width, maintaining aspect ratio."""
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    ratio = GIF_W / img.width
    new_h = int(img.height * ratio)
    return img.resize((GIF_W, new_h), Image.LANCZOS)


def save_trajectory_gif(images: list[bytes], output_path: Path):
    """Save a sequence of screenshots as a GIF."""
    frames = [resize_for_gif(img) for img in images]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_DELAY_MS,
        loop=0,
        optimize=True,
    )


def main():
    total_saved = 0

    for app_name in APPS:
        print(f"\n{'='*60}")
        print(f"Processing {app_name}...")

        # Collect all trajectories from both sources
        all_trajectories = {}

        local = get_local_screenshots(app_name)
        if local:
            all_trajectories.update(local)
            print(f"  Local: {len(local)} trajectories")

        report = extract_screenshots_from_report(app_name)
        if report:
            # Prefix to avoid collisions with local
            for tid, imgs in report.items():
                key = f"{tid}__report"
                if key not in all_trajectories:
                    all_trajectories[key] = imgs
            print(f"  Report.html: {len(report)} trajectories")

        if not all_trajectories:
            print(f"  No trajectories found, skipping")
            continue

        # Score by visual diversity and sort
        scored = []
        for tid, images in all_trajectories.items():
            diversity = compute_visual_diversity(images)
            scored.append((diversity, tid, images))

        scored.sort(reverse=True)  # Most diverse first

        # Save all GIFs, with diversity score in filename
        app_dir = OUTPUT_DIR / app_name
        app_saved = 0
        for rank, (diversity, tid, images) in enumerate(scored):
            # Clean up task ID for filename
            clean_tid = tid.replace("__", "_").replace("/", "_")
            filename = f"{rank+1:02d}_div{diversity:.1f}_{clean_tid}_{len(images)}frames.gif"
            output_path = app_dir / filename
            save_trajectory_gif(images, output_path)
            app_saved += 1

        print(f"  Saved {app_saved} GIFs to {app_dir.relative_to(REPO)}")
        print(f"  Most diverse: {scored[0][1]} (diversity={scored[0][0]:.1f}, {len(scored[0][2])} frames)")
        if len(scored) > 1:
            print(f"  Least diverse: {scored[-1][1]} (diversity={scored[-1][0]:.1f}, {len(scored[-1][2])} frames)")
        total_saved += app_saved

    print(f"\n{'='*60}")
    print(f"Total: {total_saved} GIFs saved to {OUTPUT_DIR.relative_to(REPO)}/")
    print(f"\nFiles are named: {{rank}}_div{{diversity}}_{{task_id}}_{{frames}}frames.gif")
    print(f"Higher diversity score = more visually varied screenshots")
    print(f"Browse the folders and pick the ones you like!")


if __name__ == "__main__":
    main()
