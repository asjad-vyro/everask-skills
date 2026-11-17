---
name: Brand Colour Palette Generator
description: >
  Turns one brand hex colour into a full 50-950 shade scale, light and dark mode colour tokens, measured WCAG contrast checks, ready-to-paste Tailwind v4 CSS and a swatch preview page.
  Use it for "make a palette from #0F766E", "brand colour tokens", "Tailwind shades for my brand colour", "dark mode colours", "is my brand colour accessible".
---

# Brand Colour Palette Generator

A good result is a palette the user can paste straight into a site: the exact brand colour sits in the scale, every background token has a matching text token, dark mode is remapped (not just inverted), and every contrast figure was computed by the script, never estimated.

## Step 1: Get the hex

Take the brand hex from the user's message (`#RRGGBB` or `#RGB`). If they gave a colour name or a logo instead of a hex, pick the closest hex yourself and say that you did. If they gave several colours, build the palette for the main one and say the others can be run the same way. Do not ask questions; decide and state the assumption.

## Step 2: Run the generator

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox, and the script is `scripts/palette.py`. Use the full path in the command below, where it says `SKILL_DIR`. If `skill_view` gives no path, find `palette.py` under `~/.computer/skills` with `search_files`.

```
mkdir -p /tmp/.scratch/brand-color-palette && python3 SKILL_DIR/scripts/palette.py "<HEX>" --out /tmp/.scratch/brand-color-palette
```

Optional: `--name brand` renames the scale (`--color-brand-600` instead of `--color-primary-600`).

The script prints markdown tables (scale, tokens, light and dark contrast) and the CSS, and writes `palette.css`, `palette.html` and `palette.json` into the output folder. It anchors the exact brand hex on the nearest shade, picks the primary and link colours that pass contrast, and chooses white or dark text for buttons by measured ratio. If it exits with an "invalid hex" message, fix the hex and run again.

## Step 3: Read the results and decide what to say

1. Note which shade the brand hex landed on. That is the "brand shade".
2. Look for any `FAIL` rows in the contrast tables. If there are none, say so. If there are, say what failed, what the ratio was, and the one-line fix (use a darker shade for text, put dark text on the button, use the link token instead of the plain brand colour). Do not edit the generated values unless a fix is needed, and if you change one, recompute its ratio by running the script's `ratio` logic in `execute_code` (all sums in code, never mental maths).
3. If the user asked for a particular accessibility level (AAA, government, healthcare), compare the AAA column and call out the pairs that only reach AA.
4. If the user described the brand's feel, apply it in words only: conservative brands use the darker shades for buttons, playful ones keep full saturation, minimal ones use the colour sparingly. Do not invent facts about their brand.

## Step 4: Publish the preview

Call `publish_artifact` with `kind: "html_preview"` on `/tmp/.scratch/brand-color-palette/palette.html` and a name such as `<brand-hex>-palette.html`. It is a single self-contained page with the scale, light and dark previews and both contrast tables. Publish the CSS as a second file only if the user asked for a file; otherwise the CSS goes in the reply.

## Step 5: Write the reply

The reply itself holds the deliverable, in this order:

1. One sentence: the brand hex, the shade it sits on, and any assumption you made.
2. **Shade scale**: the 11-row table from the script (shade, hex).
3. **Semantic tokens**: the light and dark token table from the script.
4. **Contrast**: the key pairs for light and dark (body text, primary button, muted text, links, input border, focus ring) with the script's ratios and results, then the fixes from Step 3, or "no failures".
5. **CSS**: the full Tailwind v4 block from the script in one `css` code block. Mention that dark mode switches on when `class="dark"` is on the `<html>` element, and that the `--color-*` variables also work in plain CSS with `var(--color-primary-600)`.
6. **Using it**: three short lines of usage, for example `bg-primary text-primary-foreground`, `bg-card text-card-foreground border-border`, `text-muted-foreground`.
7. The link to the published preview page.

## Rules

- Every hex and every ratio comes from the script output. Never type a shade or a contrast figure from memory, and never reuse numbers from another palette.
- Every background token has a paired foreground token. Say so if the user asks to change one.
- Dark mode uses a brighter primary shade and an off-white text shade, not pure white; surfaces get lighter as they rise.
- WCAG minimums used: 4.5:1 for normal text, 3:1 for large text, input borders, focus rings and button edges. A decorative border has no minimum, and the script labels it as information only.
- If the user did not ask for dark mode, still include it in the output: it costs nothing and the tokens are shared.
- Contrast results describe colours only. They are not a full accessibility audit of the user's site.
