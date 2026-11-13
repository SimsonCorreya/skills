---
name: image-to-vector
description: Recreate a logo, icon, character, mascot or emblem from a reference image as accurate SVG vector art, restyle it (flat icon, soft 3D, cinematic metal, recoloured editions), and optionally animate it (idle, thinking, talking with lip-sync, paused). Traces the reference's own pixels instead of drawing by eye, proves the match with an overlay, and gets the design approved through previewed variants before building it into anything. Use this whenever someone wants an SVG, vector, icon or mascot that should look like a picture they have, converts a PNG or JPG to SVG, says a drawing "doesn't look like" the reference, asks to trace or outline an image, wants a recoloured or "dark edition" of a known design, or wants an animated mascot for a web page, an app or a Claude Code mod, even if they never say "trace" or "vector".
---

# Image to vector

Turns a reference image into SVG that matches it, then into the styled (and, if wanted, animated) artwork the person asked for.

In the commands below, `<skill>` is this skill's folder, the one holding this file. Use `python3` where `python` isn't Python 3. The `-I` flag keeps Python from importing stray files from the image's folder.

## Why this workflow exists

Drawing a recognisable shape by typing coordinates "by eye" fails, even when it feels close. Every estimated point drifts a little, the drifts add up, and the result reads as a generic shape rather than the thing. People notice at once ("it looks nothing like it"). Tracing the reference's own pixels gives the exact geometry, and every later step (colours, shading, animation) builds on shapes that are already right.

Two habits matter as much as the tracing:

- **Prove the match before claiming it.** Set your output beside the reference and lay it over the reference. Never say "this matches your image" without having looked at that overlay. Saying it when it doesn't match costs more trust than the drawing itself.
- **Get the design approved before building it in.** Show variants as rendered previews and let the person choose. Changing a preview is cheap; changing integrated code is not, and a design the person hasn't seen tends to be rejected.

## Setup

The scripts need Python 3.9+ with Pillow, NumPy and scikit-image, Node 18+, and (for previews) Edge, Chrome or Chromium. Check with:

```bash
python -c "import PIL, numpy, skimage" && node --version
```

If the Python packages are missing, ask before installing anything. `pip install -r <skill>/requirements.txt` installs them, or `uv run --with pillow --with numpy --with scikit-image python ...` runs without installing.

Work in a scratch folder. Leave the reference image where it is, and don't copy it into anything that will be shared.

## The steps

### 1. Get a good reference

Flat artwork traces cleanly: a 2D drawing, a flat icon, a logo, a cartoon with solid colours and outlines. A photo or a 3D render has gradients and reflections that break into speckles. If all you have is a photo, ask for (or, with the person's OK, search for) a flat drawing of the same subject. A clean "how to draw X: final step" image is ideal. Use the photo only to guide shading later.

Look at the image yourself first. Name its parts in plain words (for an owl: ear tufts, face discs, eyes, beak, belly, wings) so you can talk about them with the person.

### 2. Sample its colours

```bash
python -I <skill>/scripts/palette.py <image>
```

This prints the image size, the subject's bounding box, the dominant colours, and a starter palette. Turn that into a trace config: one named colour per flat region (`body`, `belly`, `eye`, `line`, `background`, ...). Small regions (a beak, a highlight) may be below the starter's cut-off, so check the image for them. Note anti-aliased edge colours too: a dark outline often comes out as two or three dark shades. Give each its own palette entry and put them in the same layer.

### 3. Trace

Write the config (`references/config.md` documents every key, and `examples/owl/owl.config.json` is a working example) and run:

```bash
python -I <skill>/scripts/trace.py <image> <config.json> <out-dir>
```

Each pixel goes to its nearest palette colour. Each layer's connected regions are outlined (marching squares on a lightly blurred mask, so edges are smooth), simplified, and written to `<out-dir>/regions.json` as SVG path data in the image's own pixel coordinates. A `silhouette` layer (everything that isn't background) is always included. It also writes `trace.svg`, a flat-colour SVG of the result, and `classes.png`, showing which colour each pixel went to. Look at `classes.png` when a region comes out wrong. The table at the end of `references/config.md` lists the usual fixes.

### 4. Prove the match

```bash
node <skill>/scripts/compare.mjs <out-dir>/regions.json <image> <config.json> <out-dir>/compare.html
python -I <skill>/scripts/render.py <out-dir>/compare.html <out-dir>/compare.png --size 1160x520
```

The config's `compareColours` maps each layer to the reference's own colour, so the rebuild should look like the original. The page shows the reference, the rebuild, and the rebuild laid over the reference at 55% with the silhouette outlined in blue. Look at the PNG and check honestly: the outline, every region, the lines and their weight. Fix the config and re-trace until they agree. Show the person this comparison too. It's what earns their trust in what follows.

If all they wanted was an SVG of the image, `trace.svg` is it: hand it over with the comparison, and stop here unless they want more.

### 5. Restyle into three variants

Build three genuinely different renderings of the same traced shapes, in the colours the person asked for. `references/styles.md` has the recipes:

- **A, Flat icon:** flat fills, bold outlines, a two-tone light/shade split. Crispest at small sizes.
- **B, Soft 3D:** each region gets its own top-left-lit gradient, plates lift with a soft drop shadow, a glossy shell, glowing details.
- **C, Cinematic metal:** multi-band brushed gradients, bevelled edges, reflection streaks, bloom.

Recolouring (a "dark edition", say) is a palette swap on the same layers. Every region keeps its shape, and that is why it still reads as the original.

Make a preview page showing each variant large on a dark background and a light one, at the sizes it will really be used (an avatar at 72 px and 40 px, a favicon at 32 px and 16 px, and so on), plus the original colours for comparison. Render it to PNG with `render.py`, look at it yourself, and show it to the person in whatever way your environment allows (an image or file they can open, an artifact, a side panel). Ask them to choose, or to mix (C's finish with A's outlines, say). Don't build anything in yet.

### 6. Animate (optional, after a style is chosen)

Read `references/animation.md`. In short: a mood per state (idle, thinking, talking, paused), CSS keyframes for loops, and SMIL `<animate>` for anything timed to data, such as lip-sync to a speech-loudness envelope. Preview the moods live as an HTML page, and send a still PNG as well. Get approval again.

### 7. Build it in

Only now touch the project. Turn the traced shapes into a code module rather than pasting path data around:

```bash
node <skill>/scripts/emit_shapes.mjs <out-dir>/regions.json <target>/shapes.ts --name OWL_SHAPES --layers silhouette,body,wings=wing[],eyes=eye,ink
```

`key=layer` renames a layer, and `[]` keeps its regions as an array so each can be shaded on its own. The module also exports `OWL_SHAPES_VIEWBOX`. Keep coordinates in the reference's pixel space and frame them with that `viewBox`. Embedding notes are in `references/animation.md`, and notes for Claude Code mods are in `references/claude-code-mods.md`.

## Talking to the person

- Show, don't describe. Every design step ends with an image they can see.
- When they say it looks wrong, believe them. Compare against the reference and say specifically what differs before changing anything.
- Explain the method in plain words if they ask how you make it ("I sort every pixel by colour, trace each colour's outline, and turn the outlines into vector shapes").
- For a trademarked character or a company's logo, tracing it for personal use is fine. Mention once, without lecturing, that publishing or selling it is a different matter.
