#!/usr/bin/env python3
"""Launch all app servers on separate ports and serve a home page linking to each.

Usage:
    python3 serve_all.py                        # home :9000, apps :9001+
    python3 serve_all.py --test-mode            # apps start with test panel sidebar
    python3 serve_all.py --port 8000            # custom base port
    python3 serve_all.py --host 0.0.0.0         # bind all interfaces

Local access (copy the ssh command printed at startup):
    ssh -N -L 9000:localhost:9000 -L 9001:localhost:9001 ... ec2-user@<HOST>
"""

import argparse
import http.server
import json
import signal
import socketserver
import subprocess
import sys
import textwrap
from pathlib import Path

APPS_DIR = Path(__file__).parent / "apps"
SKIP_DIRS = {"app-description", "user-manuals"}


def discover_apps():
    apps = []
    for app_dir in sorted(APPS_DIR.iterdir()):
        if not app_dir.is_dir() or app_dir.name in SKIP_DIRS:
            continue
        if not (app_dir / "server.py").exists() or not (app_dir / "index.html").exists():
            continue

        title = app_dir.name.replace("-", " ").title()
        desc_file = app_dir / "APP_DESCRIPTION.md"
        if desc_file.exists():
            for line in desc_file.read_text().splitlines()[:10]:
                if line.startswith("#"):
                    raw = line.lstrip("#").strip()
                    for suffix in [" — App Description", " - App Description"]:
                        if raw.endswith(suffix):
                            raw = raw[: -len(suffix)]
                    title = raw
                    break

        task_count = 0
        tasks_file = app_dir / "real-tasks.json"
        if tasks_file.exists():
            try:
                task_count = len(json.loads(tasks_file.read_text()))
            except Exception:
                pass

        apps.append({
            "name": app_dir.name,
            "dir": str(app_dir),
            "title": title,
            "task_count": task_count,
        })
    return apps


def build_homepage(apps, host, base_port):
    origin = f"http://{host}" if host != "0.0.0.0" else "http://localhost"

    cards = []
    for app in apps:
        url = f"{origin}:{app['port']}"
        initials = "".join(w[0] for w in app["title"].split()[:2]).upper()
        badge = (
            f'<span class="badge">{app["task_count"]} tasks</span>'
            if app["task_count"] else ""
        )
        cards.append(f"""\
        <a class="card" href="{url}" target="_blank">
          <div class="icon">{initials}</div>
          <div class="info">
            <div class="title">{app["title"]}</div>
            <div class="meta">
              <span class="port">:{app["port"]}</span>
              {badge}
            </div>
          </div>
          <div class="arrow">&#8599;</div>
        </a>""")

    return textwrap.dedent(f"""\
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mirror-Mirror</title>
    <style>
      *{{margin:0;padding:0;box-sizing:border-box}}
      body{{
        font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
        background:#0f0f17;color:#e0e0e8;min-height:100vh;padding:48px 24px;
      }}
      .container{{max-width:720px;margin:0 auto}}
      h1{{font-size:1.8rem;font-weight:700;margin-bottom:4px;color:#fff}}
      .subtitle{{color:#888;font-size:.95rem;margin-bottom:32px}}
      .grid{{display:flex;flex-direction:column;gap:8px}}
      .card{{
        display:flex;align-items:center;gap:14px;padding:14px 18px;
        background:#1a1a28;border:1px solid #2a2a3a;border-radius:10px;
        text-decoration:none;color:inherit;transition:border-color .15s,background .15s;
      }}
      .card:hover{{border-color:#5a5af0;background:#1e1e30}}
      .icon{{
        width:40px;height:40px;border-radius:8px;
        background:linear-gradient(135deg,#3a3af0,#7a5af8);
        display:flex;align-items:center;justify-content:center;
        font-weight:700;font-size:.85rem;color:#fff;flex-shrink:0;letter-spacing:.5px;
      }}
      .info{{flex:1;min-width:0}}
      .title{{font-weight:600;font-size:.95rem;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
      .meta{{display:flex;gap:10px;margin-top:3px;font-size:.8rem;color:#666}}
      .port{{font-family:'SF Mono',Menlo,monospace;color:#5a5af0}}
      .badge{{background:#1e2e1e;color:#6abf69;padding:1px 8px;border-radius:8px;font-size:.75rem}}
      .arrow{{color:#444;font-size:1.1rem;flex-shrink:0;transition:color .15s}}
      .card:hover .arrow{{color:#5a5af0}}
    </style>
    </head>
    <body>
    <div class="container">
      <h1>Mirror-Mirror</h1>
      <p class="subtitle">{len(apps)} apps &middot; ports {base_port + 1}&ndash;{base_port + len(apps)}</p>
      <div class="grid">
    {chr(10).join(cards)}
      </div>
    </div>
    </body>
    </html>""")


class HomeHandler(http.server.BaseHTTPRequestHandler):
    html = ""
    app_count = 0

    def do_GET(self):
        if self.path == "/api/health":
            body = json.dumps({"status": "ok", "apps": self.app_count}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            body = self.html.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    def log_message(self, format, *args):
        pass


def main():
    parser = argparse.ArgumentParser(description="Launch all Mirror-Mirror app servers")
    parser.add_argument("--port", type=int, default=9000, help="Base port (home page); apps get port+1, port+2, ... (default: 9000)")
    parser.add_argument("--host", default="localhost", help="Bind address (default: localhost)")
    parser.add_argument("--test-mode", action="store_true", help="Start app servers with in-browser test panel")
    args = parser.parse_args()

    apps = discover_apps()
    if not apps:
        print("No apps found in apps/")
        sys.exit(1)

    processes = []

    def cleanup(sig=None, frame=None):
        print(f"\nStopping {len(processes)} servers...")
        for p in processes:
            try:
                p.terminate()
            except OSError:
                pass
        for p in processes:
            try:
                p.wait(timeout=3)
            except subprocess.TimeoutExpired:
                p.kill()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    # Start each app server
    print(f"Starting {len(apps)} app servers...")
    for i, app in enumerate(apps):
        port = args.port + 1 + i
        app["port"] = port
        cmd = [sys.executable, "server.py", "--port", str(port)]
        if args.test_mode:
            cmd.append("--test-mode")
        proc = subprocess.Popen(
            cmd,
            cwd=app["dir"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        processes.append(proc)
        print(f"  :{port}  {app['title']}")

    # Build and serve home page
    html = build_homepage(apps, args.host, args.port)
    HomeHandler.html = html
    HomeHandler.app_count = len(apps)

    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer((args.host, args.port), HomeHandler)

    host_display = args.host if args.host != "0.0.0.0" else "localhost"
    last_port = args.port + len(apps)

    # Print SSH tunnel command
    ports = " ".join(f"-L {p}:localhost:{p}" for p in range(args.port, last_port + 1))
    print(f"\nServing at http://{host_display}:{args.port}")
    if args.test_mode:
        print("Test mode: enabled")
    print(f"\nSSH tunnel (run on your local machine):")
    print(f"  ssh -N {ports} -i ~/.ssh/mirror-mirror.pem ec2-user@<HOST>")
    print(f"\nPress Ctrl+C to stop.\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    main()
