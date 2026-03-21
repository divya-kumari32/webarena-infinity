#!/usr/bin/env python3
"""Build a dense, edge-to-edge collage GIF from selected trajectories.

Tightly packed, varied sizes, heavy overlaps, no gaps visible.
Inspired by the example in analysis/output/example.png.
"""

import base64
import io
import json
import random
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parent.parent
S3_RESULTS = REPO / "analysis" / "s3_results"
LOCAL_APPS = REPO / "apps"
OUTPUT_DIR = REPO / "analysis" / "output"
TRAJ_DIR = OUTPUT_DIR / "trajectories"

FRAME_DELAY_MS = 500
CANVAS_W = 2600
CANVAS_H = 1600
MAX_FRAMES = 30

SELECTIONS = [
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


# ── Source extraction ───────────────────────────────────────────────────

def extract_task_from_report(app_name, task_id):
    app_dir = S3_RESULTS / app_name
    if not app_dir.is_dir():
        return []
    reports = list(app_dir.rglob("report.html"))
    if not reports:
        return []
    p5 = [r for r in reports if "p5" in r.parent.name or "p5" in r.parent.parent.name]
    latest = max(p5 or reports, key=lambda p: p.stat().st_mtime)
    html = latest.read_text()
    pat = re.compile(r"<code>(task_[ehm]?\d+)</code>")
    positions = [(m.start(), m.group(1)) for m in pat.finditer(html)]
    for idx, (pos, tid) in enumerate(positions):
        if tid != task_id:
            continue
        end = positions[idx + 1][0] if idx + 1 < len(positions) else len(html)
        chunk = html[pos:end]
        images = []
        for m in re.finditer(r"data:image/png;base64,([A-Za-z0-9+/=]+)", chunk):
            try:
                b = base64.b64decode(m.group(1))
                Image.open(io.BytesIO(b)).verify()
                images.append(b)
            except Exception:
                continue
        return images
    return []


def get_local_task(app_name, task_id, run_prefix):
    local_name = "linear-account-settings" if app_name == "linear-account-settings-v2" else app_name
    results_dir = LOCAL_APPS / local_name / "results"
    if not results_dir.is_dir():
        return []
    for run_dir in results_dir.iterdir():
        if not run_dir.is_dir() or (run_prefix and not run_dir.name.startswith(run_prefix)):
            continue
        ss_dir = run_dir / task_id / "screenshots"
        if not ss_dir.is_dir():
            continue
        steps = sorted(ss_dir.glob("step_*.png"), key=lambda p: int(p.stem.split("_")[1]))
        if steps:
            return [s.read_bytes() for s in steps]
    return []


def extract_gif_frames(gif_path):
    img = Image.open(gif_path)
    frames = []
    for i in range(img.n_frames):
        img.seek(i)
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="PNG")
        frames.append(buf.getvalue())
    return frames


def parse_selection(path):
    parts = path.split("/")
    app, filename = parts[0], parts[1]
    if app == "figma-slides-browsing":
        return {"app": app, "source": "browsing"}
    m = re.match(r"\d+_div[\d.]+_(task_[ehm]?\d+)_(.+)_\d+frames\.gif", filename)
    if not m:
        return {"app": app, "source": "gif"}
    task_id, source_part = m.group(1), m.group(2)
    if source_part == "report":
        return {"app": app, "source": "report", "task_id": task_id}
    return {"app": app, "source": "local", "task_id": task_id, "run_prefix": source_part}


def resolve_frames(sel):
    info = parse_selection(sel)
    gif_path = TRAJ_DIR / sel
    if info["source"] == "browsing":
        pngs = sorted(gif_path.parent.glob("*.png"))
        return [p.read_bytes() for p in pngs] if pngs else extract_gif_frames(gif_path)
    if info["source"] == "report":
        frames = extract_task_from_report(info["app"], info["task_id"])
        if frames:
            return frames
    if info["source"] == "local":
        frames = get_local_task(info["app"], info["task_id"], info.get("run_prefix", ""))
        if frames:
            return frames
    return extract_gif_frames(gif_path)


# ── Dense collage layout ────────────────────────────────────────────────

def fit_full(img_bytes, target_w, target_h):
    """Resize to fit the full viewport inside the target area (no cropping).

    If aspect ratios differ, the image is letterboxed with the BG color.
    """
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    ratio = min(target_w / img.width, target_h / img.height)
    new_w, new_h = int(img.width * ratio), int(img.height * ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    if new_w == target_w and new_h == target_h:
        return img
    canvas = Image.new("RGB", (target_w, target_h), (12, 12, 20))
    canvas.paste(img, ((target_w - new_w) // 2, (target_h - new_h) // 2))
    return canvas


def generate_dense_layout(n_cells, seed=42):
    """Hand-crafted dense tiling that fills the entire canvas.

    Returns list of (x, y, w, h) rects covering the canvas edge-to-edge,
    with varied sizes and overlaps.
    """
    rng = random.Random(seed)

    # Define placement rects manually for a 16-cell dense mosaic
    # that fills 2600x1600 with varied sizes and overlaps.
    # Think of it as layered — background tiles first, then overlapping
    # foreground pieces on top.

    # Dense tiling with 16:10 aspect ratio cells (matching 1440x900 screenshots).
    # All cells use w:h = 16:10 so the full viewport is shown without cropping.
    # Sizes: large=720x450, medium=560x350, small=432x270
    rects = [
        # (x, y, w, h, z_order)
        # Row 0: top edge
        (-20, -15, 720, 450, 0),
        (620, -25, 560, 350, 0),
        (1120, -10, 720, 450, 0),
        (1780, -20, 560, 350, 0),
        (2220, -10, 432, 270, 0),

        # Row 1: middle band (staggered)
        (-15, 380, 560, 350, 1),
        (480, 340, 720, 450, 1),
        (1120, 360, 560, 350, 1),
        (1620, 310, 720, 450, 2),
        (2200, 250, 432, 270, 1),

        # Row 2: lower band
        (-10, 690, 720, 450, 2),
        (630, 730, 560, 350, 2),
        (1100, 700, 720, 450, 2),
        (1740, 720, 560, 350, 3),
        (2180, 680, 480, 300, 2),

        # Row 3: bottom
        (-20, 1080, 720, 450, 3),
        (620, 1060, 560, 350, 3),
        (1100, 1040, 720, 450, 3),
        (1740, 1060, 560, 350, 3),
        (2200, 1020, 432, 270, 3),
    ]

    # Add jitter to each rect
    placements = []
    for i, (x, y, w, h, z) in enumerate(rects[:n_cells]):
        jx = rng.randint(-30, 30)
        jy = rng.randint(-25, 25)
        # Vary size slightly
        sw = int(w * rng.uniform(0.92, 1.08))
        sh = int(h * rng.uniform(0.92, 1.08))
        placements.append({
            "x": x + jx, "y": y + jy,
            "w": sw, "h": sh,
            "z": z + rng.random() * 0.5,
        })

    # Paint order: back to front
    order = sorted(range(len(placements)), key=lambda i: placements[i]["z"])
    return placements, order


def build_collage_frame(cell_frames, placements, paint_order, frame_idx):
    """Render one dense collage frame. No borders, no shadows, just screenshots."""
    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (20, 20, 30))

    for ci in paint_order:
        if ci >= len(cell_frames):
            continue
        p = placements[ci]
        frames = cell_frames[ci]
        fi = frame_idx % len(frames)

        img = fit_full(frames[fi], p["w"], p["h"])

        # Add a 1px dark edge so overlapping cells are distinguishable
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.rectangle([(0, 0), (img.width - 1, img.height - 1)], outline=(15, 15, 22), width=1)

        canvas.paste(img, (p["x"], p["y"]))

    return canvas


def load_layout(layout_path):
    """Load layout from editor-exported JSON."""
    with open(layout_path) as f:
        layout = json.load(f)
    # Layout is sorted by z; we need selections list and placements
    sels = [item["path"] for item in layout]
    placements = [{"x": item["x"], "y": item["y"], "w": item["w"], "h": item["h"], "z": item["z"]} for item in layout]
    paint_order = sorted(range(len(layout)), key=lambda i: placements[i]["z"])
    return sels, placements, paint_order


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--layout", type=str, help="Path to editor-exported layout JSON")
    args = parser.parse_args()

    if args.layout:
        print(f"Loading layout from {args.layout}...")
        sels, placements, paint_order = load_layout(args.layout)
    else:
        rng = random.Random(42)
        sels = list(SELECTIONS)
        rng.shuffle(sels)
        placements, paint_order = generate_dense_layout(len(sels), seed=42)

    print("Resolving frames...")
    cell_frames = []
    for sel in sels:
        app = sel.split("/")[0]
        frames = resolve_frames(sel)
        print(f"  {app}: {len(frames)} frames")
        cell_frames.append(frames)

    # Export layout JSON for the editor
    layout_export = []
    for i, (sel, p) in enumerate(zip(sels, placements)):
        app = sel.split("/")[0]
        print(f"  [{i}] {app}: {p['w']}x{p['h']} at ({p['x']},{p['y']}) z={p['z']}")
        label = app.replace("-", " ").title()
        layout_export.append({"path": sel, "label": label, "x": p["x"], "y": p["y"], "w": p["w"], "h": p["h"], "z": p["z"]})
    layout_export.sort(key=lambda item: item["z"])
    layout_path = OUTPUT_DIR / "trajectories" / "current_layout.json"
    with open(layout_path, "w") as f:
        json.dump(layout_export, f, indent=2)
    print(f"\nLayout saved to {layout_path}")

    n_frames = min(max(len(f) for f in cell_frames), MAX_FRAMES)
    print(f"\nBuilding {n_frames} frames at {CANVAS_W}x{CANVAS_H}...")

    frames = []
    for fi in range(n_frames):
        if fi % 5 == 0:
            print(f"  Frame {fi+1}/{n_frames}...")
        frame = build_collage_frame(cell_frames, placements, paint_order, fi)
        frames.append(frame)

    # Save GIF
    gif_path = OUTPUT_DIR / "trajectory_collage.gif"
    frames[0].save(
        gif_path, save_all=True, append_images=frames[1:],
        duration=FRAME_DELAY_MS, loop=0, optimize=True,
    )
    print(f"\nGIF: {gif_path} ({gif_path.stat().st_size / 1024 / 1024:.1f}MB)")

    # Save PNG frames
    frames_dir = OUTPUT_DIR / "trajectory_collage_frames"
    frames_dir.mkdir(exist_ok=True)
    for f in frames_dir.glob("*.png"):
        f.unlink()
    for i, frame in enumerate(frames):
        frame.save(frames_dir / f"frame_{i:03d}.png", optimize=True)
    print(f"PNGs: {frames_dir}/ ({n_frames} frames)")

    # MP4
    mp4_path = OUTPUT_DIR / "trajectory_collage.mp4"
    try:
        subprocess.run([
            "ffmpeg", "-y", "-framerate", "2",
            "-i", str(frames_dir / "frame_%03d.png"),
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "18", "-preset", "slow", str(mp4_path),
        ], capture_output=True, check=True)
        print(f"MP4: {mp4_path} ({mp4_path.stat().st_size / 1024 / 1024:.1f}MB)")
    except Exception as e:
        print(f"MP4 failed: {e}")


if __name__ == "__main__":
    main()
