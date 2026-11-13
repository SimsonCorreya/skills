# Style recipes

Three renderings of one trace. The layer names below are examples (`silhouette`, `shell`, `plates` for the main coloured regions, `eyes` for glowing details, `ink` for outlines). Use whatever the trace produced. `each(list, attrs)` means one `<path d=… fill-rule="evenodd" attrs/>` per region.

The trick behind all three: gradients default to `gradientUnits="objectBoundingBox"`, so **one gradient applied to many paths shades each path inside its own box**. Every plate becomes a lit facet with no extra geometry. A single overlay clipped to the silhouette then adds the light across the whole subject.

Pick a light direction (top-left is natural) and keep every highlight, shadow and gradient consistent with it.

## Palette swaps

Recolouring is a mapping per layer, and the shapes don't change. Keep the contrast between neighbouring layers. A "black edition" of a red-and-gold design works because the shell becomes near-black (#2A2E34 to #0B0C0E) while the plates become a light gunmetal (#E6E9ED to #6A7078): dark against light, just as red was against gold. If two neighbours end up close in value, the design turns to mush at small sizes.

Glowing details (eyes, lights) keep one saturated hue with a near-white core: #2FB2FF glow, #E4F7FF core.

## A: Flat icon

Flat fills, bold outlines, and a two-tone split for light and shade. Crispest at 16–40 px.

```xml
<defs><clipPath id="right"><rect x="{centreX}" y="0" width="9999" height="9999"/></clipPath></defs>
<!-- silhouette in the outline colour: the gaps between regions become outlines -->
{each(silhouette, 'fill="#0A0B0D"')}
{each(shell, 'fill="#2C3036"')}
<g clip-path="url(#right)" opacity=".45">{each(shell, 'fill="#121417"')}</g>
{each(plates, 'fill="#AEB4BC"')}
<g clip-path="url(#right)">{each(plates, 'fill="#8C929A"')}</g>
{each(eyes, 'fill="#DDF5FF" stroke="#2FB2FF" stroke-width="1.1"')}
{each(ink, 'fill="#0A0B0D"')}
```

## B: Soft 3D

Each plate gets its own top-left-lit gradient and lifts off the shell with a soft shadow. The shell is glossy and the details glow. Quiet and premium, it suits Apple-style UI.

```xml
<defs>
  <clipPath id="whole"><path d="{silhouette joined}"/></clipPath>
  <radialGradient id="shell" cx="30%" cy="18%" r="90%">
    <stop offset="0" stop-color="#5E646C"/><stop offset=".45" stop-color="#25282D"/><stop offset="1" stop-color="#0B0C0E"/>
  </radialGradient>
  <linearGradient id="plate" x1="0" y1="0" x2=".55" y2="1">
    <stop offset="0" stop-color="#E6E9ED"/><stop offset=".55" stop-color="#A3A9B1"/><stop offset="1" stop-color="#6A7078"/>
  </linearGradient>
  <linearGradient id="light" x1="0" x2="1">  <!-- lit left, shaded right -->
    <stop offset="0" stop-color="#fff" stop-opacity=".1"/><stop offset=".5" stop-color="#000" stop-opacity="0"/>
    <stop offset="1" stop-color="#000" stop-opacity=".38"/>
  </linearGradient>
  <filter id="lift"><feDropShadow dx="0" dy="1.2" stdDeviation="1.2" flood-opacity=".55"/></filter>
  <filter id="glow" x="-50%" y="-150%" width="200%" height="400%">
    <feGaussianBlur stdDeviation="2.4" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="blur"><feGaussianBlur stdDeviation="2"/></filter>
</defs>
{each(silhouette, 'fill="#08090A"')}
{each(shell, 'fill="url(#shell)"')}
<g filter="url(#lift)">{each(plates, 'fill="url(#plate)"')}</g>
{each(ink, 'fill="#101114" opacity=".85"')}
<g clip-path="url(#whole)">
  <rect {subject box} fill="url(#light)"/>
  <path d="{a soft crescent on the upper-left of the dome}" fill="#fff" opacity=".28" filter="url(#blur)"/>
</g>
{each(eyes, 'fill="#2FB2FF" filter="url(#glow)"')}
{each(eyes, 'fill="#E4F7FF"')}
```

## C: Cinematic metal

Brushed multi-band gradients, bevelled edges, a reflection streak and bloom. Closest to a photo or 3D render, and busiest at small sizes.

```xml
<linearGradient id="shell" x1=".1" y1="0" x2=".9" y2="1">  <!-- glossy black: bands of light and dark -->
  <stop offset="0" stop-color="#666C74"/><stop offset=".25" stop-color="#22252A"/><stop offset=".5" stop-color="#08090B"/>
  <stop offset=".7" stop-color="#2A2E34"/><stop offset="1" stop-color="#050506"/>
</linearGradient>
<linearGradient id="plate" x1="0" y1="0" x2="1" y2="1">  <!-- brushed gunmetal -->
  <stop offset="0" stop-color="#F1F3F6"/><stop offset=".28" stop-color="#8E949C"/><stop offset=".48" stop-color="#CDD2D8"/>
  <stop offset=".72" stop-color="#5A6068"/><stop offset="1" stop-color="#9AA0A8"/>
</linearGradient>
<linearGradient id="bevel" x1="0" y1="0" x2="1" y2="1">  <!-- a stroke that is light top-left, dark bottom-right -->
  <stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset=".4" stop-color="#fff" stop-opacity="0"/>
  <stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".8"/>
</linearGradient>
<radialGradient id="spill"><stop offset="0" stop-color="#2FB2FF" stop-opacity=".55"/><stop offset="1" stop-color="#2FB2FF" stop-opacity="0"/></radialGradient>
```

Apply them like this:
- **Regions:** `each(shell, 'fill="url(#shell)" stroke="url(#bevel)" stroke-width="1.2"')`, and the same with `#plate` for the plates at a stroke width of 1.4.
- **Overlays clipped to the silhouette:**
  - the light gradient, at up to .45 on the shaded side
  - a skewed white polygon at .18 with a blur, as a reflection streak
  - elliptical `#spill` patches where glowing details light the plates
- **Bloom on the details:** a blur of 3.2 merged three times, with a near-white core on top.

## Previewing variants

- **One iframe per SVG.** Each SVG's ids (`#shell`, `#glow`) must not collide with another's on the same page, so wrap each in its own `<iframe srcdoc=…>`.
- **Dark and light.** Show every variant on a dark background (#1f1f1e) and a light one (#f4f3ee).
- **The original colours.** Show it in the reference's own colours too, so the person can judge the shape apart from the recolouring.
- **The sizes it will really be used at.** Detail that reads at 300 px can turn to mud at 40 px.
