---
name: design-driven-pptx
description: >
  Generate .pptd presentations from a user-provided design.md (visual design system) + content source (docx/outline).
  The skill orchestrates a multi-agent workflow where the main agent adapts the design system into a PPTD theme,
  creates the outline and .pptd master file, then dispatches subagents to build .page files in parallel.
  Use this skill when the user provides a design.md (or similar visual specification) and wants it turned into
  a PPTX presentation with multi-agent parallel execution. Also use when the user explicitly requests
  reusing a design system for PPT generation.
---

# Design-Driven PPTX Skill

Generate PPTD presentations from a `design.md` visual design system + content source.

## When to Use

- User provides a `design.md` file (visual design system) + content document/outline
- User requests multi-agent PPT creation with a specific design
- User wants to reuse a design system for different content

## Inputs

Required files (user-provided):
- `design.md` — Visual design system (colors, typography, layout, components)
- Content source — Word doc, markdown outline, or structured text

## Workflow Overview

1. **Read inputs** — Parse design.md and content source
2. **Adapt design** — Map design.md to PPTD theme (read `references/design-adapter.md`)
3. **Create outline** — Build `outline.md` from content (read `references/main-agent-workflow.md` step 3)
4. **Create .pptd** — Write master entry file with theme + page list
5. **Build .page files** — Dispatch subagents in parallel (read `references/subagent-prompts.md`)
6. **Check & fix** — Run checker, fix errors/warnings
7. **Deliver** — Return .pptd artifact

## Key Rules

- **Main agent** personally completes steps 1-4 (design, outline, .pptd). Never delegate these.
- **Subagents** only build .page files.
- Content must follow the user's source exactly — no additions, no deletions.
- All .page files use `pageType`: cover | table_of_contents | chapter | content | final.
- `content.text` must use YAML block scalar `|`.
- Single-line text boxes must set `wrap: false`.
- Every element must have a `layer` field (-1=bg, 0=container, 1=content, 2=fg).
- `bounds: [x, y, w, h]` is the coordinate format.
- All files go under `<work-dir>/` with `pages/` subdirectory.

## File Structure

```
<work-dir>/
  design.md              # (user-provided, optional copy)
  outline.md             # generated
  <name>.pptd            # generated master file
  pages/
    cover.page
    toc.page
    ch01_title.page
    ch01_content.page
    ...
```

## Convert to PPTX

After the .pptd project is complete, convert it to .pptx using the built-in converter:

```bash
python3 {skill_path}/scripts/pptd2pptx.py <work-dir>/<name>.pptd [<output.pptx>]
```

Requirements:
- `python-pptx` (install via `pip install python-pptx`)
- `PyYAML` (install via `pip install pyyaml`)
- `resvg` (optional, for SVG decoration support: `pip install resvg`)

The converter supports:
- Text boxes with rich HTML (`<p>`, `<span>`, `<strong>`, `<em>`, `<u>`, `<s>`, `<sup>`, `<sub>`, `<a>`, `<ul>`, `<ol>`, `<li>`)
- Shapes (rect, roundRect, ellipse, triangle, diamond, star5, plus, arrow, flowchart shapes, etc.)
- Images (local paths and URLs)
- Tables with theme styling
- Charts (bar, line, pie, scatter, bubble, combo — fully rendered with theme colors + seriesStyle)
- Tables with theme styling (header/body fill, border, font)
- Freeform shapes (SVG path commands M/L/C/Q/Z with rotation)
- SVG Decorations (pattern, background, accent, divider — auto-rendered to PNG via resvg)
- Icons (rendered as placeholder label)
- Backgrounds (solid, gradient, image)
- Theme colors & text styles
- Borders, fills, rotations, shadows, opacity
- Animations (fade, wipe, flyIn, peekIn, growShrink — per-element with click/withPrevious/afterPrevious triggers)
- CJK font fallback via `a:ea` element

## Progressive Loading

Load references only when needed:
- Before step 2: read `references/design-adapter.md` (includes dynamic color adaptation)
- Before step 3: read `references/main-agent-workflow.md` (step 3 section)
- Before step 5: read `references/subagent-prompts.md`
- For chart generation: read `references/chart-guide.md`
- For dynamic colors: read `references/dynamic-color-adaptation.md`
- For layout templates: read `references/design-adapter.md` Section 6
- For PPTD format: read `format/pptd.md`
- For subagent notes: read `guideline/subagent/attention.md`
- For outline template: read `assets/outline-template.md`
