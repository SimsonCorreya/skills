"""Screenshots an HTML (or SVG) page with a headless Chromium browser.

Usage: python -I render.py <page.html> <out.png> [--size 1200x800] [--wait 600]

--wait is the page's virtual time in milliseconds before the shot: raise it to
catch an animation further along, or to let iframes and images load. Local
files may load other local files (the reference image), so the page can show
it beside the trace.

The browser is found in this order: the CHROME_PATH environment variable, the
usual Edge / Chrome / Chromium install locations, then the PATH.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

local = os.environ.get("LOCALAPPDATA", "")
CANDIDATES = [
    os.environ.get("CHROME_PATH", ""),
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.join(local, r"Google\Chrome\Application\chrome.exe") if local else "",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
]
ON_PATH = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "msedge", "chrome")


def find_browser() -> str:
    for candidate in CANDIDATES:
        if candidate and Path(candidate).exists():
            return candidate
    for name in ON_PATH:
        found = shutil.which(name)
        if found:
            return found
    sys.exit(
        "No Chromium browser found (Edge, Chrome or Chromium). Install one or set CHROME_PATH, "
        "or open the page and screenshot it by hand."
    )


parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("page")
parser.add_argument("out")
parser.add_argument("--size", default="1200x800", help="window size, WIDTHxHEIGHT")
parser.add_argument("--wait", type=int, default=600, help="virtual time in ms before the screenshot")
args = parser.parse_args()

width, height = args.size.lower().split("x")
page = Path(args.page).resolve().as_uri()
out = Path(args.out).resolve()
out.unlink(missing_ok=True)
result = subprocess.run(
    [
        find_browser(),
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--allow-file-access-from-files",
        f"--virtual-time-budget={args.wait}",
        f"--window-size={width},{height}",
        f"--screenshot={out}",
        page,
    ],
    check=False,
    capture_output=True,
    text=True,
    timeout=120,
)
if not out.exists():
    sys.exit(f"no screenshot written to {out}\n{result.stderr[-2000:]}")
print(f"wrote {out}")
