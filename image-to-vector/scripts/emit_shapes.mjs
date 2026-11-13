// Turns a trace (regions.json) into a code module of SVG path data, so the
// project imports the shapes instead of pasting path strings around.
//
// Usage: node emit_shapes.mjs <regions.json> <out.ts|out.js> --name SHAPES --layers <spec>
//
// <spec> is a comma list of `key` or `key=layer`, with `[]` after the layer
// to keep its regions as an array (one path each, so each can be shaded on
// its own) instead of one joined path:
//   --layers silhouette,shell,plates=gold[],eyes=eye,ink
import { readFileSync, writeFileSync } from 'node:fs'

const args = process.argv.slice(2)
const option = flag => {
  const at = args.indexOf(flag)
  return at >= 0 ? args[at + 1] : undefined
}
const [regionsPath, outPath] = args
const name = option('--name') ?? 'SHAPES'
const spec = option('--layers')
if (!regionsPath || !outPath || !spec) {
  console.error('usage: node emit_shapes.mjs <regions.json> <out> --name SHAPES --layers silhouette,shell,plates=gold[],eyes=eye,ink')
  process.exit(2)
}

const regions = JSON.parse(readFileSync(regionsPath, 'utf8'))
const isTypeScript = outPath.endsWith('.ts')
const [width, height] = regions.size
if (!regions.silhouette.length) throw new Error(`nothing was traced in ${regionsPath}`)
const boxes = regions.silhouette.map(r => r.bbox)
const box = [
  Math.min(...boxes.map(b => b[0])),
  Math.min(...boxes.map(b => b[1])),
  Math.max(...boxes.map(b => b[2])),
  Math.max(...boxes.map(b => b[3])),
]

const margin = 6
const vx = Math.max(0, box[0] - margin)
const vy = Math.max(0, box[1] - margin)
const viewBox = `${vx} ${vy} ${Math.min(width, box[2] + margin) - vx} ${Math.min(height, box[3] + margin) - vy}`

const entries = spec.split(',').map(part => {
  const [key, source = key] = part.split('=')
  const isArray = source.endsWith('[]')
  const layer = source.replace(/\[\]$/, '')
  const list = regions[layer]
  if (!list) throw new Error(`no layer "${layer}" in ${regionsPath}`)
  return isArray
    ? `  ${key}: [\n${list.map(r => `    ${JSON.stringify(r.d)},`).join('\n')}\n  ],`
    : `  ${key}: ${JSON.stringify(list.map(r => r.d).join(' '))},`
})

writeFileSync(
  outPath,
  [
    `// Traced from a reference image (${width} x ${height} px); coordinates are its pixels.`,
    `// The subject spans x ${box[0]}-${box[2]}, y ${box[1]}-${box[3]}. Generated: trace again`,
    `// rather than editing these by hand. Draw each with fill-rule="evenodd".`,
    '',
    `export const ${name} = {`,
    ...entries,
    `}${isTypeScript ? ' as const' : ''}`,
    '',
    `// The subject's box with a small margin, ready for <svg viewBox={${name}_VIEWBOX}>.`,
    `export const ${name}_VIEWBOX = ${JSON.stringify(viewBox)}`,
    '',
  ].join('\n'),
)
console.log(`wrote ${outPath}`)
