// Rebuilds a trace in the reference's own colours and sets it beside, and
// over, the reference: the proof that the trace matches.
//
// Usage: node compare.mjs <regions.json> <image> <colours.json | config.json> <out.html>
//
// colours.json maps layer names to fills, drawn in its key order, e.g.
//   { "silhouette": "#1A0705", "shell": "#83272A", "gold": "#FCCC06", "eye": "#D7EEFA", "ink": "#1A0705" }
// Filling the silhouette with the outline colour first makes the gaps between
// regions read as the reference's outlines.
import { readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { pathToFileURL } from 'node:url'

const [regionsPath, imagePath, coloursPath, outPath] = process.argv.slice(2)
if (!outPath) {
  console.error('usage: node compare.mjs <regions.json> <image> <colours.json> <out.html>')
  process.exit(2)
}
const regions = JSON.parse(readFileSync(regionsPath, 'utf8'))
// A trace config with a `compareColours` entry works as well as a colours file.
const coloursFile = JSON.parse(readFileSync(coloursPath, 'utf8'))
const colours = coloursFile.compareColours ?? (coloursFile.palette ? null : coloursFile)
if (!colours) {
  console.error('the config has no "compareColours": add one mapping each layer to the reference colour (see references/config.md)')
  process.exit(2)
}
const [width, height] = regions.size
const image = pathToFileURL(resolve(imagePath)).href

// Frame the subject with a little margin (the whole image if nothing was traced).
const boxes = regions.silhouette.length ? regions.silhouette.map(r => r.bbox) : [[0, 0, width, height]]
const x0 = Math.max(0, Math.min(...boxes.map(b => b[0])) - 6)
const y0 = Math.max(0, Math.min(...boxes.map(b => b[1])) - 6)
const x1 = Math.min(width, Math.max(...boxes.map(b => b[2])) + 6)
const y1 = Math.min(height, Math.max(...boxes.map(b => b[3])) + 6)
const view = `${x0} ${y0} ${x1 - x0} ${y1 - y0}`
const shownHeight = 440
const shownWidth = Math.round((shownHeight * (x1 - x0)) / (y1 - y0))

const rebuild = Object.entries(colours)
  .map(([layer, fill]) => (regions[layer] ?? []).map(r => `<path d="${r.d}" fill="${fill}" fill-rule="evenodd"/>`).join(''))
  .join('')
const svg = body =>
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${view}" width="${shownWidth}" height="${shownHeight}">${body}</svg>`
const original = `<image href="${image}" x="0" y="0" width="${width}" height="${height}"/>`
const outline = regions.silhouette.map(r => `<path d="${r.d}" fill="none" stroke="#00B3FF" stroke-width="1"/>`).join('')

writeFileSync(
  outPath,
  `<!doctype html><meta charset="utf-8"><title>Trace check</title><style>
body{margin:0;padding:20px;font:14px Segoe UI,-apple-system,sans-serif;background:#fff;display:flex;gap:28px}
figure{margin:0;text-align:center}</style>
<figure>${svg(original)}<figcaption>Reference</figcaption></figure>
<figure>${svg(rebuild)}<figcaption>Traced vectors</figcaption></figure>
<figure>${svg(original + `<g opacity=".55">${rebuild}</g>` + outline)}<figcaption>Overlay (trace at 55% over the reference)</figcaption></figure>`,
)
console.log(`wrote ${outPath}`)
