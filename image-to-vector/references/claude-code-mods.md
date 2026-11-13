# Claude Code mods

Read this only when the art goes into a Claude Code mod's UI (the `plugin-authoring` skill, where installed, has the full API). These notes come from building an animated mascot into one, and may change as the mod API evolves.

- **The `Svg` element.** It draws on desktop, VS Code and phone, but not in the terminal; give the terminal a text fallback. Pass `isInteractive` so CSS and SMIL run (a script-less frame), and keep `source` under 131,072 characters. `width` and `height` are CSS pixels, and the markup should use `width="100%" height="100%"` with a `viewBox`.
- **The end-of-turn box covers the band above the prompt.** On desktop, when a turn ends, the next-step box covers the whole `AbovePrompt` area, and a band can't show there even compact. To keep something visible, also draw it under the latest reply: a `ui.render` hook on `AssistantMessage`, matching the block against the `turn.complete` answer.
- **The validator wants helpers at top level.** `claude plugin validate` requires every helper that receives `$` to be declared at module top level.
- **Keep the shapes in a generated module** (`emit_shapes.mjs`). The art then lives in one file, and re-tracing means regenerating that file.
