# Animating the art

Animate only a design the person has approved. Then preview the animation and get approval again before building it in.

## Moods

Give the art a few states and change the whole SVG document when the state changes:

| Mood | Feels like | Typical motion |
| --- | --- | --- |
| idle | alive, at rest | a slow hover (translateY ±2–3%), a blink every ~5 s, a slight glance or tilt, a light sweep across the plates every ~7 s |
| thinking | busy, processing | a rotating HUD ring of dashed circles, a scan line across the eyes, quicker pulsing |
| talking | speaking | details glowing with the voice, a nod or bob, a voice meter |
| paused | waiting | dimmed details, a slower hover, a pulsing pause badge |

Draw the static artwork once (a constant), and add only each mood's extras and CSS.

## CSS for loops, SMIL for timed data

- **CSS `@keyframes`** for anything that loops forever, such as a hover, a blink or a sweep. It's cheap and easy to read.
- **SMIL** (`<animate>`, `<animateTransform>`) for motion that follows data over a set time, like lip-sync: `values="a;b;c…" dur="6.2s" calcMode="linear" fill="freeze"`.
- **A negative `begin`** starts partway through, when resuming at a known offset: `begin="-1.62s"`. Subtract a lead of about 120 ms to cover the time the frame takes to load.
- **For previews,** use `repeatCount="indefinite"` instead of `fill="freeze"`, so the sample loops.

## Lip-sync from speech loudness

Have whatever produces the audio report the loudness of each sentence as one digit (0–9) per 50 ms:

```python
step = int(rate * 0.05)
rms = np.sqrt(np.mean(padded.reshape(-1, step) ** 2, axis=1))
share = rms / (rms.max() or 1)
digits = np.where(share < 0.08, 0, np.clip(np.round(9 * share ** 0.7), 1, 9))
```

Send it with the sentence's duration and the offset it starts at. Map each digit to motion:
- a mouth or slit glow: `scale(1, 0.4 + 1.6·level)` and opacity `0.15 + 0.85·level`
- the eyes: opacity `0.7 + 0.3·level`
- a bob: `translate(0, −5·level)`
- meter bars: `scaleY(0.15 + 0.85·level)`, each bar a step behind the last, for a ripple

To restart the same sentence (a seek, a resume, a speed change), the document has to change. Put a counter in a comment (`<!--talking 7-->`) so the frame reloads and the animation begins again.

## Size limits

Long sentences make long `values` lists, roughly ten characters per step for each animated element. Average the envelope down to at most about 400 steps per document. Measure the largest document you can produce: a detailed helmet traced this way came to about 30 KB of art, and the talking mood added roughly 10–25 KB.

## Transform pitfalls

- **Origins on SVG elements.** CSS `transform-origin` on an SVG element is in that element's user units. Give each rotating or scaling group an explicit origin in px (`transform-origin:152px 190px`). Elements inside a scaled `<g>` take origins in the scaled group's own units.
- **One transform per element.** CSS animation and a `transform` attribute fight over the same element. Nest a `<g>` for each source of motion: float, then tilt, then bounce, then the art.
- **Reduced motion.** Respect it: `@media (prefers-reduced-motion:reduce){*{animation:none!important}}`.

## Previewing animation

- **Live:** an HTML page with each mood in its own `<iframe srcdoc>` plays the animation. Open it in a browser, or send it however your environment shows HTML (a file the person opens, an artifact, a side panel), and it plays.
- **Still frames:** `render.py --wait <ms>` captures the page at that point in virtual time. Take two or three moments to check the motion, and send one PNG as well, since some viewers (a phone, say) don't run the page.

## Embedding

- **Keep the shapes in a generated module** (`scripts/emit_shapes.mjs`). The art then lives in one file, and re-tracing means regenerating that file.
- **Web pages and apps:** inline the SVG (so CSS can reach its parts) or use it as an `<img>` (simpler, but no CSS animation from outside). Size it with CSS and keep the `viewBox`.
- **Claude Code mods:** see `claude-code-mods.md`.
