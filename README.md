# skills

Skills for [Claude Code](https://claude.com/claude-code). Each folder is one self-contained skill: a `SKILL.md` with the instructions Claude follows, plus any scripts and references it uses.

| Skill | What it does |
| --- | --- |
| [image-to-vector](image-to-vector/) | Recreates a logo, icon or mascot from a reference image as accurate SVG. It traces the image's pixels instead of drawing by eye, proves the match with an overlay, restyles the result (flat, soft 3D, metal, recoloured), and can animate it. |

## Install

### As a plugin (recommended)

In Claude Code, add this repo as a marketplace once, then install the skills you want:

```
/plugin marketplace add SimsonCorreya/skills
/plugin install image-to-vector@skills
```

Or from a terminal:

```bash
claude plugin marketplace add SimsonCorreya/skills
claude plugin install image-to-vector@skills
```

To pick up new skills and updates later, run `/plugin marketplace update skills`.

### By copying a folder

Copy a skill's folder into your skills directory, either for every project or for one:

```bash
git clone https://github.com/SimsonCorreya/skills.git
cp -r skills/image-to-vector ~/.claude/skills/
# or: cp -r skills/image-to-vector <project>/.claude/skills/
```

Some skills need extra tools, such as Python packages. Each skill's own README lists them.

## Using a skill

You don't call a skill by name. Ask for what you want ("make an SVG of this logo"), and Claude loads the skill whose description matches. You can also load it directly: `/image-to-vector` for a copied folder, or `/image-to-vector:image-to-vector` when it's installed as a plugin (plugin skills carry the plugin's name as a prefix).

## Adding a skill

1. Make a folder named after the skill, in lowercase with hyphens, holding a `SKILL.md` with `name` and `description` frontmatter. Never put a `SKILL.md` at the repo root.
2. Add an entry to `.claude-plugin/marketplace.json`:
   ```json
   { "name": "my-skill", "source": "./my-skill", "description": "One line on what it does.", "version": "1.0.0" }
   ```
3. Add a row to the table above.
4. Bump a skill's `version` in `marketplace.json` when you change it, so installed copies update.

## License

[MIT](LICENSE)
