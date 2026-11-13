"""Traces a flat reference image into SVG path regions, one layer per colour group.

Usage: python -I trace.py <image> <config.json> <out dir>

Every pixel is assigned to the nearest colour in the config's palette. Each
layer (a group of palette colours) is cleaned up, split into connected
regions, outlined with marching squares on a lightly blurred mask (smooth
edges, not pixel steps), simplified, and written as SVG path data in the
image's own pixel coordinates.

Writes to <out dir>:
  regions.json  { "size": [w, h], "silhouette": [...], "<layer>": [...], "ink": [...] }
                each list holding regions { "area", "bbox": [x0, y0, x1, y1], "d" },
                largest first, holes kept (draw with fill-rule="evenodd")
  trace.svg     the layers stacked in flat colours: a first, usable SVG
  classes.png   each pixel painted its assigned palette colour, to check the
                classification when a region comes out wrong

The config format is described in references/config.md.
"""

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from skimage import filters, measure, morphology

RESERVED = {"size", "silhouette", "ink"}


# Version-independent clean-up helpers (scikit-image has renamed the size
# arguments of remove_small_objects / remove_small_holes across releases).
def drop_small(mask: np.ndarray, min_size: int) -> np.ndarray:
    if min_size <= 1 or not mask.any():
        return mask
    labelled = measure.label(mask, connectivity=1)
    sizes = np.bincount(labelled.ravel())
    keep = sizes >= min_size
    keep[0] = False
    return keep[labelled]


def fill_holes(mask: np.ndarray, max_size: int) -> np.ndarray:
    """Fills holes (background pockets) smaller than max_size pixels."""
    return ~drop_small(~mask, max_size) if max_size > 0 else mask


def close(mask: np.ndarray, radius: int) -> np.ndarray:
    # Pad first so closing doesn't eat into shapes that touch the image edge.
    padded = np.pad(mask, radius + 1)
    closed = morphology.closing(padded, morphology.disk(radius))
    return closed[radius + 1 : -radius - 1, radius + 1 : -radius - 1]


def trace(mask: np.ndarray, min_area: int, tolerance: float, grow: float = 0.0) -> list[dict]:
    """Outlines each connected region. grow (pixels, may be negative) moves the
    outline outwards by a fraction of a pixel, to win back anti-aliased edges."""
    sigma = 0.9
    # For a blurred step edge, the contour at this level sits `grow` pixels outside the edge.
    level = 0.5 * (1 - math.erf(grow / (sigma * math.sqrt(2))))
    regions = []
    labelled = measure.label(mask, connectivity=1)
    for region in measure.regionprops(labelled):
        if region.area < min_area:
            continue
        y0, x0, y1, x1 = region.bbox
        # Work on the region's own box (plus a margin for the blur) rather than the whole image.
        own = np.pad(region.image, 3).astype(float)
        # A light blur before tracing gives smooth edges instead of pixel steps.
        contours = measure.find_contours(filters.gaussian(own, sigma=sigma), level)
        parts = []
        for contour in contours:
            simple = measure.approximate_polygon(contour, tolerance=tolerance)
            if len(simple) < 3:
                continue
            points = "L".join(f"{x + x0 - 3:.1f},{y + y0 - 3:.1f}" for y, x in simple)
            parts.append("M" + points + "Z")
        if parts:
            regions.append({"area": int(region.area), "bbox": [int(x0), int(y0), int(x1), int(y1)], "d": " ".join(parts)})
    return sorted(regions, key=lambda r: -r["area"])


def classify(rgb: np.ndarray, centres: np.ndarray) -> np.ndarray:
    """Nearest palette colour for every pixel, a band of rows at a time to bound memory."""
    height = rgb.shape[0]
    label = np.empty(rgb.shape[:2], dtype=np.int16)
    step = max(1, 4_000_000 // max(1, rgb.shape[1] * len(centres)))
    for top in range(0, height, step):
        band = rgb[top : top + step]
        label[top : top + step] = ((band[:, :, None, :] - centres[None, None, :, :]) ** 2).sum(axis=3).argmin(axis=2)
    return label


def hex_colour(rgb: list[int]) -> str:
    return "#" + "".join(f"{int(c):02X}" for c in rgb)


def write_svg(out: dict, config: dict, path: Path) -> None:
    palette = config["palette"]
    colours = config.get("compareColours")
    if not colours:
        # No explicit colours: the silhouette takes the ink colour (so gaps read as
        # outlines), each layer its first palette colour, ink on top.
        ink_colours = (config.get("ink") or {}).get("colours") or []
        colours = {}
        if ink_colours:
            colours["silhouette"] = hex_colour(palette[ink_colours[0]])
        for layer in config.get("layers", []):
            colours[layer["name"]] = hex_colour(palette[layer["colours"][0]])
        if ink_colours:
            colours["ink"] = hex_colour(palette[ink_colours[0]])
    width, height = out["size"]
    boxes = [r["bbox"] for r in out["silhouette"]] or [[0, 0, width, height]]
    x0 = max(0, min(b[0] for b in boxes) - 6)
    y0 = max(0, min(b[1] for b in boxes) - 6)
    x1 = min(width, max(b[2] for b in boxes) + 6)
    y1 = min(height, max(b[3] for b in boxes) + 6)
    groups = []
    for layer, fill in colours.items():
        regions = out.get(layer) or []
        if regions:
            paths = "".join(f'<path d="{r["d"]}"/>' for r in regions)
            groups.append(f'<g id="{layer}" fill="{fill}" fill-rule="evenodd">{paths}</g>')
    path.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1 - x0} {y1 - y0}" '
        f'width="{x1 - x0}" height="{y1 - y0}">\n' + "\n".join(groups) + "\n</svg>\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("image")
    parser.add_argument("config")
    parser.add_argument("out_dir")
    args = parser.parse_args()
    image_path, config_path, out_dir = Path(args.image), Path(args.config), Path(args.out_dir)

    config = json.loads(config_path.read_text(encoding="utf-8"))
    out_dir.mkdir(parents=True, exist_ok=True)
    palette: dict[str, list[int]] = config["palette"]
    names = list(palette)
    background_name = config.get("background", "background")
    if background_name not in names:
        sys.exit(f'the palette has no "{background_name}" entry: add the background colour to it')
    background = names.index(background_name)
    for layer in config.get("layers", []):
        if layer["name"] in RESERVED:
            sys.exit(f'"{layer["name"]}" is reserved: give that layer another name')

    rgba = np.asarray(Image.open(image_path).convert("RGBA")).astype(float)
    alpha = rgba[:, :, 3:4] / 255
    # Transparent images: blend onto the background colour, so soft edges classify sensibly.
    rgb = rgba[:, :, :3] * alpha + np.array(palette[background_name], dtype=float) * (1 - alpha)
    height, width, _ = rgb.shape
    centres = np.array([palette[name] for name in names], dtype=float)
    label = classify(rgb, centres)
    label[rgba[:, :, 3] < 128] = background
    if config.get("backgroundFromEdges", True) and len(names) > 1:
        # Background-coloured pixels the subject encloses (white eyes, a white
        # highlight) are part of the subject: give them their nearest other colour.
        pockets = measure.label(label == background, connectivity=1)
        edges = np.concatenate([pockets[0], pockets[-1], pockets[:, 0], pockets[:, -1]])
        enclosed = (pockets > 0) & ~np.isin(pockets, np.unique(edges))
        if enclosed.any():
            others = [at for at in range(len(names)) if at != background]
            nearest = classify(rgb[enclosed][None], centres[others])[0]
            label[enclosed] = np.array(others)[nearest]
    for x0, y0, x1, y1 in config.get("ignore", []):
        label[y0:y1, x0:x1] = background

    colours = np.array([palette[name] for name in names], dtype=np.uint8)
    Image.fromarray(colours[label]).save(out_dir / "classes.png")
    print("pixels per colour:", {name: int((label == at).sum()) for at, name in enumerate(names)})

    def is_any(group: list[str]) -> np.ndarray:
        unknown = [name for name in group if name not in names]
        if unknown:
            sys.exit(f"colours not in the palette: {unknown}")
        return np.isin(label, [names.index(name) for name in group])

    # Defaults scale with the image, so a 64 px icon and a 2000 px drawing both trace.
    pixels = width * height
    subject = fill_holes(label != background, config.get("silhouetteFillHoles", round(pixels * 0.0035)))
    silhouette_min = config.get("silhouetteMinArea", max(16, round(pixels * 0.002)))
    out: dict[str, object] = {"size": [width, height], "silhouette": trace(subject, silhouette_min, 0.5, config.get("silhouetteGrow", 0.0))}

    for layer in config.get("layers", []):
        mask = is_any(layer["colours"])
        if layer.get("close"):
            mask = close(mask, layer["close"])
        mask = drop_small(mask, 8)
        if layer.get("fillHoles"):
            mask = fill_holes(mask, layer["fillHoles"])
        if layer.get("notNear"):
            mask &= ~morphology.dilation(is_any(layer["notNear"]), morphology.disk(1))
        out[layer["name"]] = trace(mask, layer.get("minArea", 20), layer.get("tolerance", 0.5), layer.get("grow", 0.0))

    ink_config = config.get("ink")
    if ink_config:
        ink = is_any(ink_config["colours"])
        # Thick patches of an ink colour are areas, not lines: drop them, keep the lines.
        if ink_config.get("dropThickerThan"):
            ink &= ~morphology.opening(ink, morphology.disk(ink_config["dropThickerThan"]))
        ink = drop_small(ink, ink_config.get("minArea", 30))
        out["ink"] = trace(ink, ink_config.get("minArea", 30), ink_config.get("tolerance", 0.35), ink_config.get("grow", 0.0))

    (out_dir / "regions.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    write_svg(out, config, out_dir / "trace.svg")
    for key, value in out.items():
        if key != "size":
            regions = value if isinstance(value, list) else []
            print(f"{key}: {len(regions)} regions", [(r["area"], r["bbox"]) for r in regions[:6]])
    print(f"wrote {out_dir / 'regions.json'}, {out_dir / 'trace.svg'}, {out_dir / 'classes.png'}")


if __name__ == "__main__":
    main()
