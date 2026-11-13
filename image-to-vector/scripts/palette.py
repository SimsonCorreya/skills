"""Prints a reference image's dominant colours, the box its subject fills, and a
starter palette for a trace config.

Usage: python -I palette.py <image> [--top 14] [--min-share 0.3]

Colours are grouped into bins of 16 per channel and listed by pixel count, with
one sample pixel's exact value for each. The background is the corner colour
(or full transparency); the subject box is everything else.
"""

import argparse
import json
from collections import Counter

import numpy as np
from PIL import Image

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("image")
parser.add_argument("--top", type=int, default=14, help="how many colour bins to list")
parser.add_argument("--min-share", type=float, default=0.3, help="percent of pixels a bin needs to make the starter palette")
args = parser.parse_args()

source = Image.open(args.image)
has_alpha = source.mode in ("RGBA", "LA", "PA") or (source.mode == "P" and "transparency" in source.info)
rgba = np.asarray(source.convert("RGBA")).astype(int)
rgb, alpha = rgba[:, :, :3], rgba[:, :, 3]
height, width, _ = rgb.shape
print(f"size: {width} x {height}" + ("  (has transparency: transparent pixels count as background)" if has_alpha else ""))

if has_alpha and (alpha < 128).any():
    background = alpha < 128
    corner = None
else:
    corner = rgb[0, 0]
    background = (np.abs(rgb - corner).sum(axis=2) < 30) | (rgb.min(axis=2) > 235)

ys, xs = np.where(~background)
if len(xs):
    source_note = "transparency" if corner is None else f"corner colour {corner.tolist()}"
    print(f"subject box: x {xs.min()}-{xs.max()}, y {ys.min()}-{ys.max()} (background from {source_note})")
else:
    print("subject box: nothing found apart from the background")

opaque = alpha >= 128
bins = rgb // 16
counts = Counter(map(tuple, bins[opaque].reshape(-1, 3)))
total = max(1, int(opaque.sum()))
print("dominant colours (count, share, sample RGB):")
starter: dict[str, list[int]] = {}
if corner is not None or has_alpha:
    starter["background"] = corner.tolist() if corner is not None else [255, 255, 255]
for (r, g, b), count in counts.most_common(args.top):
    where = np.argwhere((bins[:, :, 0] == r) & (bins[:, :, 1] == g) & (bins[:, :, 2] == b) & opaque)
    y, x = where[len(where) // 2]
    share = 100 * count / total
    sample = rgb[y, x].tolist()
    print(f"  {count:8d} ({share:4.1f}%)  {sample}  e.g. at x={x}, y={y}")
    # Near-duplicates (anti-aliased shades of one colour) fold into the first, larger entry.
    is_duplicate = any(np.linalg.norm(np.array(sample) - np.array(kept)) < 30 for kept in starter.values())
    if share >= args.min_share and not is_duplicate:
        starter[f"colour{len(starter)}"] = sample

print("\nstarter palette (rename each entry for the region it is; add edge shades the list above shows if they misclassify):")
print(json.dumps({"palette": starter}, indent=1).replace("\n   ", " ").replace("\n  ]", "]"))
