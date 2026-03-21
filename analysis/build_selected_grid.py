#!/usr/bin/env python3
"""Build a high-resolution grid GIF from user-selected trajectories.

Re-extracts frames from original sources (report.html / local PNGs) at full
resolution, then composites into a grid.

Usage:
    python analysis/build_selected_grid.py --selections selections.json
"""

import base64
import io
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
S3_RESULTS = REPO / "analysis" / "s3_results"
LOCAL_APPS = REPO / "apps"
OUTPUT_DIR = REPO / "analysis" / "output"
TRAJ_DIR = OUTPUT_DIR / "trajectories"

# Cell size per GIF in the grid (high resolution)
CELL_W = 640
CELL_H = 400
LABEL_HEIGHT = 26
GAP = 4
FRAME_DELAY_MS = 500

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
    "figma-slides-browsing": "Figma Slides",
    "elation-patient-communication": "Elation Comms",
    "gmail-accounts-and-contacts": "Gmail Contacts",
    "figma-text-and-typography": "Figma Typography",
    "clio-matters": "Clio Matters",
    "elation-clinical-records": "Elation Clinical",
    "shopify-web-performance": "Shopify Perf",
}


def extract_task_from_report(app_name: str, task_id: str) -> list[bytes]:
    """Re-extract a specific task's screenshots from report.html at full quality."""
    app_dir = S3_RESULTS / app_name
    if not app_dir.is_dir():
        return []

    reports = list(app_dir.rglob("report.html"))
    if not reports:
        return []

    p5_reports = [r for r in reports if "p5" in r.parent.name or "p5" in r.parent.parent.name]
    pool = p5_reports if p5_reports else reports
    latest = max(pool, key=lambda p: p.stat().st_mtime)

    html = latest.read_text()
    task_pattern = re.compile(r"<code>(task_[ehm]?\d+)</code>")
    task_positions = [(m.start(), m.group(1)) for m in task_pattern.finditer(html)]

    for idx, (pos, tid) in enumerate(task_positions):
        if tid != task_id:
            continue
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
        return images

    return []


def get_local_task(app_name: str, task_id: str, run_prefix: str) -> list[bytes]:
    """Get a specific task's screenshots from local results."""
    local_name = app_name
    if app_name == "linear-account-settings-v2":
        local_name = "linear-account-settings"

    results_dir = LOCAL_APPS / local_name / "results"
    if not results_dir.is_dir():
        return []

    for run_dir in results_dir.iterdir():
        if not run_dir.is_dir():
            continue
        if run_prefix and not run_dir.name.startswith(run_prefix):
            continue
        task_dir = run_dir / task_id
        if not task_dir.is_dir():
            continue
        ss_dir = task_dir / "screenshots"
        if not ss_dir.is_dir():
            continue
        steps = sorted(ss_dir.glob("step_*.png"), key=lambda p: int(p.stem.split("_")[1]))
        if steps:
            return [s.read_bytes() for s in steps]

    return []


def get_browsing_frames(gif_path: Path) -> list[bytes]:
    """Extract frames from a browsing GIF (figma-slides-browsing PNGs)."""
    parent = gif_path.parent
    pngs = sorted(parent.glob("*.png"))
    if pngs:
        return [p.read_bytes() for p in pngs]
    # Fallback: read from the GIF itself
    return extract_gif_frames(gif_path)


def extract_gif_frames(gif_path: Path) -> list[bytes]:
    """Extract frames from an existing GIF file."""
    img = Image.open(gif_path)
    frames = []
    for i in range(img.n_frames):
        img.seek(i)
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="PNG")
        frames.append(buf.getvalue())
    return frames


def parse_selection(gif_rel_path: str) -> dict:
    """Parse a selected GIF path into app_name, task_id, source info."""
    parts = gif_rel_path.split("/")
    app_name = parts[0]
    filename = parts[1]

    # Special case: browsing screenshots
    if app_name == "figma-slides-browsing":
        return {"app": app_name, "source": "browsing", "task_id": None, "run_prefix": None}

    # Parse filename: {rank}_div{div}_{task_id}_{source}_{frames}frames.gif
    # Examples:
    #   03_div18.1_task_h3_claude-cu_20260316_225748_para_9frames.gif  -> local
    #   03_div17.7_task_h67_report_21frames.gif                        -> report
    m = re.match(r"\d+_div[\d.]+_(task_[ehm]?\d+)_(.+)_\d+frames\.gif", filename)
    if not m:
        return {"app": app_name, "source": "gif", "task_id": None, "run_prefix": None}

    task_id = m.group(1)
    source_part = m.group(2)

    if source_part == "report":
        return {"app": app_name, "source": "report", "task_id": task_id, "run_prefix": None}
    else:
        # Local: source_part is the run directory prefix
        return {"app": app_name, "source": "local", "task_id": task_id, "run_prefix": source_part}


def resolve_frames(gif_rel_path: str) -> list[bytes]:
    """Get full-resolution frames for a selected GIF."""
    info = parse_selection(gif_rel_path)
    gif_path = TRAJ_DIR / gif_rel_path

    if info["source"] == "browsing":
        return get_browsing_frames(gif_path)

    if info["source"] == "report" and info["task_id"]:
        frames = extract_task_from_report(info["app"], info["task_id"])
        if frames:
            return frames

    if info["source"] == "local" and info["task_id"]:
        frames = get_local_task(info["app"], info["task_id"], info["run_prefix"])
        if frames:
            return frames

    # Fallback: extract from the GIF itself
    print(f"  Falling back to GIF extraction for {gif_rel_path}")
    return extract_gif_frames(gif_path)


def resize_to_cell(img_bytes: bytes) -> Image.Image:
    """Resize to fit inside cell (letterboxed)."""
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    ratio = min(CELL_W / img.width, CELL_H / img.height)
    new_w = int(img.width * ratio)
    new_h = int(img.height * ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    cell = Image.new("RGB", (CELL_W, CELL_H), (15, 15, 24))
    cell.paste(img, ((CELL_W - new_w) // 2, (CELL_H - new_h) // 2))
    return cell


def add_label(frame: Image.Image, label: str) -> Image.Image:
    new_h = frame.height + LABEL_HEIGHT
    labeled = Image.new("RGB", (frame.width, new_h), (20, 20, 30))
    labeled.paste(frame, (0, 0))
    draw = ImageDraw.Draw(labeled)
    draw.rectangle([(0, frame.height), (frame.width, new_h)], fill=(25, 25, 40))
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), label, font=font)
    text_w = bbox[2] - bbox[0]
    text_x = (frame.width - text_w) // 2
    text_y = frame.height + (LABEL_HEIGHT - (bbox[3] - bbox[1])) // 2
    draw.text((text_x, text_y), label, fill=(200, 200, 220), font=font)
    return labeled


def build_grid_gif(cells, output_path, cols=4):
    max_frames = max(len(frames) for _, frames in cells)

    cell_frame_sets = []
    for label, raw_frames in cells:
        frames = [add_label(resize_to_cell(f), label) for f in raw_frames]
        n = len(frames)
        if n < max_frames:
            frames = [frames[i % n] for i in range(max_frames)]
        cell_frame_sets.append(frames)

    rows = (len(cells) + cols - 1) // cols
    cell_h = CELL_H + LABEL_HEIGHT
    grid_w = cols * CELL_W + (cols - 1) * GAP
    grid_h = rows * cell_h + (rows - 1) * GAP

    print(f"Building grid: {grid_w}x{grid_h}, {max_frames} frames, {len(cells)} cells")

    grid_frames = []
    for fi in range(max_frames):
        grid = Image.new("RGB", (grid_w, grid_h), (15, 15, 24))
        for ci, frames in enumerate(cell_frame_sets):
            r, c = ci // cols, ci % cols
            grid.paste(frames[fi], (c * (CELL_W + GAP), r * (cell_h + GAP)))
        grid_frames.append(grid)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save GIF
    grid_frames[0].save(
        output_path,
        save_all=True,
        append_images=grid_frames[1:],
        duration=FRAME_DELAY_MS,
        loop=0,
        optimize=True,
    )
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"Saved: {output_path} ({size_mb:.1f}MB)")

    # Also save as individual PNG frames for max quality
    frames_dir = output_path.parent / (output_path.stem + "_frames")
    frames_dir.mkdir(exist_ok=True)
    for i, frame in enumerate(grid_frames):
        frame.save(frames_dir / f"frame_{i:03d}.png", optimize=True)
    print(f"Saved {len(grid_frames)} PNG frames to {frames_dir}/")


def main():
    selections = [
        "elation-clinical-records/03_div18.1_task_h3_claude-cu_20260316_225748_para_9frames.gif",
        "elation-patient-communication/03_div17.7_task_h67_report_21frames.gif",
        "elation-prescriptions/03_div22.9_task_h13_report_29frames.gif",
        "figma-slides/02_div2.4_task_h11_report_8frames.gif",
        "figma-slides-browsing/00_all_23frames.gif",
        "gitlab-plan-and-track/24_div45.0_task_h7_report_5frames.gif",
        "gitlab-plan-and-track/44_div27.6_task_h33_report_9frames.gif",
        "gitlab-plan-and-track/78_div4.5_task_h81_report_11frames.gif",
        "gmail/02_div60.9_task_h10_gemini-cu_20260317_051226_dryr_36frames.gif",
        "gmail/01_div70.1_task_h8_kimi_20260317_012425_parallel_16frames.gif",
        "handshake-career-exploration/06_div3.3_task_h63_report_9frames.gif",
        "linear-account-settings-v2/05_div2.4_task_h74_report_19frames.gif",
        "paypal-my-wallet/01_div82.8_task_h55_report_10frames.gif",
        "paypal-my-wallet/03_div10.9_task_h64_report_4frames.gif",
        "superhuman-general/01_div8.0_task_h66_report_13frames.gif",
        "xero-invoicing/18_div1.7_task_h49_report_10frames.gif",
    ]

    cells = []
    for sel in selections:
        app = sel.split("/")[0]
        label = DISPLAY_NAMES.get(app, app)
        print(f"\nResolving: {sel}")
        info = parse_selection(sel)
        print(f"  Parsed: {info}")

        frames = resolve_frames(sel)
        if not frames:
            print(f"  ERROR: No frames found, skipping")
            continue
        print(f"  Got {len(frames)} full-res frames")
        cells.append((label, frames))

    if not cells:
        print("No cells!")
        sys.exit(1)

    cols = 4
    output = OUTPUT_DIR / "trajectory_grid_hires.gif"
    build_grid_gif(cells, output, cols=cols)


if __name__ == "__main__":
    main()
