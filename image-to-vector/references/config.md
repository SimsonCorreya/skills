# Trace config reference

`scripts/trace.py` reads one JSON file. `examples/owl/owl.config.json` is a complete, working example. Keys starting with `_` (like `_about`) are ignored, so use them for notes.

```jsonc
{
  "palette": { "background": [255, 255, 255], "body": [232, 122, 46], "line": [17, 16, 29] },
  "background": "background",
  "ignore": [[0, 392, 400, 440]],
  "layers": [ { "name": "body", "colours": ["body"], "close": 1, "fillHoles": 30, "minArea": 40, "grow": 0.8 } ],
  "ink": { "colours": ["line"], "minArea": 20 },
  "compareColours": { "silhouette": "#11101D", "body": "#E87A2E", "ink": "#11101D" }
}
```

## Top level

| Key | Default | What it does |
| --- | --- | --- |
| `palette` | required | `{name: [r, g, b]}`. Every pixel goes to the nearest entry. Include the background and every outline shade. Anti-aliased edges often need a second or third dark shade of the outline. |
| `background` | `"background"` | The palette name of the background. |
| `backgroundFromEdges` | `true` | Only background-coloured pixels connected to the image's edge count as background. Enclosed ones (white eyes, a white highlight) go to their nearest other palette colour, so give white parts their own entry (`"eye": [255, 255, 255]`). Set to `false` to treat every background-coloured pixel as background. |
| `ignore` | `[]` | `[[x0, y0, x1, y1], ...]` rectangles treated as background: a title, a caption, a watermark. |
| `silhouetteFillHoles` | 0.35% of the image | Holes in the subject's outline smaller than this many pixels are filled. |
| `silhouetteMinArea` | 0.2% of the image (min 16) | Separate pieces of the subject smaller than this are dropped. Lower it for a logo with small separate parts. |
| `silhouetteGrow` | `0` | Moves the silhouette's edge out (positive) or in (negative) by a fraction of a pixel. Around `-0.6` stops the outer outline looking heavier than the reference's. |
| `layers` | `[]` | The colour regions, drawn in this order. See below. |
| `ink` | none | Outlines and panel lines, traced as thin filled shapes drawn on top. See below. |
| `compareColours` | derived | `{layer: "#hex"}` in drawing order. Used by `compare.mjs` and for `trace.svg`. Filling `silhouette` with the outline colour first makes the gaps between regions read as outlines. Without it, `trace.svg` uses each layer's first palette colour. |

Transparent PNGs work: pixels under 50% opacity are background, and soft edges are blended onto the background colour before classifying.

## Each layer

| Key | Default | What it does |
| --- | --- | --- |
| `name` | required | The layer's key in `regions.json`. Not `size`, `silhouette` or `ink`. |
| `colours` | required | Palette names merged into this layer (a colour and its shade, say). |
| `close` | none | Morphological closing radius in pixels: fills specks of texture and hairline gaps. `1` or `2` is usually enough. |
| `fillHoles` | none | Holes smaller than this many pixels are filled. |
| `minArea` | `20` | Regions smaller than this are dropped. |
| `tolerance` | `0.5` | Path simplification in pixels. `0.3`–`0.6` is crisp; higher is smoother and smaller. |
| `notNear` | none | Palette names. The layer is cut back one pixel from them, so it doesn't creep under a neighbour. |
| `grow` | `0` | Moves the outline outwards by a fraction of a pixel. Anti-aliased edge pixels often classify as something else and get dropped, which leaves the outlines between regions looking heavier than the reference. `0.5`–`0.8` wins them back. |

## Ink

| Key | Default | What it does |
| --- | --- | --- |
| `colours` | required | Palette names of the outlines. |
| `minArea` | `30` | Specks smaller than this are dropped. Ink has no `close` or `fillHoles`: thin lines vanish under either. |
| `dropThickerThan` | none | A radius in pixels. Patches of an ink colour thicker than this are areas, not lines, and are dropped (a dark panel that shares the outline colour). Leave it out when solid dark parts, such as pupils, should stay. |
| `tolerance` | `0.35` | As for layers. Lower than layers, since lines are thin. |
| `grow` | `0` | As for layers. |

## Fixing common problems

Look at `classes.png` first: it shows which palette colour every pixel went to.

| You see | Try |
| --- | --- |
| Speckles in a shaded or textured area | That shade reads as another colour. Give it its own palette entry in the same layer, or raise the layer's `close` and `fillHoles`. |
| A white or background-coloured part is missing | Give it its own palette entry. With `backgroundFromEdges` on (the default) it's kept if the subject encloses it. If it touches the image edge, it can't be told apart from the background. |
| Outlines look heavier than the reference | `grow: 0.5`–`0.8` on the layers, `silhouetteGrow: -0.6`. |
| A layer creeps under its neighbour | `notNear` with the neighbour's colours. |
| Thin lines broken into dashes | Add the outline's lighter anti-aliased shade to the palette and to `ink.colours`. |
| A small separate part is missing | Lower `silhouetteMinArea` and that layer's `minArea`. |
| A title or caption is traced | Add an `ignore` rectangle. |
