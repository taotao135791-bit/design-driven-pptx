#!/usr/bin/env python3
"""
Enhance all styles/*/design.md files by appending `layouts:` and `decoration-grammar:` sections.

The layouts section now includes:
  - Precise pixel bounds for all elements (1280×720 canvas)
  - 12-column grid alignment rules
  - Fibonacci-based spacing for breathing room
  - Golden ratio split options for asymmetric layouts
  - Z-order rules for layering
"""

import os
from pathlib import Path

# Base directory
STYLES_DIR = Path(__file__).resolve().parent.parent / "styles"

# Classification buckets
EDITORIAL_MAGAZINE = {
    "soft-editorial", "editorial-forest", "editorial-tri-tone",
    "emerald-editorial", "vellum", "broadside", "cartesian",
}

BOLD_POSTER = {
    "coral", "bold-poster", "block-frame", "neo-grid-bold",
    "raw-grid", "studio", "signal", "peoples-platform",
}

PLAYFUL_CREATIVE = {
    "playful", "creative-mode", "daisy-days", "scatterbrain",
    "sakura-chroma", "pink-script", "pin-and-paper",
}

RETRO_NOSTALGIA = {
    "8-bit-orbit", "retro-windows", "retro-zine", "stencil-tablet",
}

PROFESSIONAL_CLEAN = {
    "blue-professional", "biennale-yellow", "cobalt-grid", "capsule",
    "mat", "grove", "long-table", "monochrome",
    "apple-demo", "corporate-blue", "tech-neon", "tech-neon-v2",
}


def get_bucket(style_name: str) -> str:
    if style_name in EDITORIAL_MAGAZINE:
        return "editorial"
    if style_name in BOLD_POSTER:
        return "bold"
    if style_name in PLAYFUL_CREATIVE:
        return "playful"
    if style_name in RETRO_NOSTALGIA:
        return "retro"
    if style_name in PROFESSIONAL_CLEAN:
        return "professional"
    return "professional"  # fallback


# ---------------------------------------------------------------------------
# Universal layouts — precise bounds for 1280×720 canvas
# ---------------------------------------------------------------------------
# Grid: 60px margin, 24px gutter, 8px baseline
# 1-col: [60, y, 1160, h]
# 2-col: [60, y, 560, h] + [660, y, 560, h]  (40px middle gutter)
# 3-col: [60, y, 360, h] + [460, y, 360, h] + [860, y, 360, h]
# Golden split minor: [60, y, 436, h] + [556, y, 664, h]
# Golden split major: [60, y, 716, h] + [836, y, 384, h]
# ---------------------------------------------------------------------------

LAYOUTS_SECTION = """
layouts:
  full-statement:
    description: "One dominant statement or conclusion fills the center of the slide. Eyebrow label above, decorative numeral or mark behind at low opacity. Used for key conclusions and manifesto moments."
    grid: "1-col, centered"
    composition:
      - elementType: shape | text
        layer: -1
        bounds: "[60, 60, 1160, 600]"
        notes: "Background color block or decorative numeral at 6% opacity, centered"
      - elementType: text
        layer: 2
        bounds: "[60, 200, 1160, 24]"
        styleRef: "label"
        notes: "Eyebrow label — uppercase, wide tracking, primary color, centered"
      - elementType: text
        layer: 1
        bounds: "[160, 260, 960, 120]"
        styleRef: "h1"
        notes: "Large display statement — 60-70% width, vertically centered, wrap: false for single-line impact"
      - elementType: shape
        layer: 2
        bounds: "[616, 400, 48, 3]"
        notes: "Small accent line centered under statement — 48×3px, primary color, 2px radius"
    breathing: "Massive vertical whitespace: 200px above eyebrow, 120px below accent line. Statement should feel isolated and authoritative."

  asymmetric-split:
    description: "Left 38% is a colored/surfaced panel with title and subtitle. Right 62% is body content on default background. Used for topic overviews and chapter introductions."
    grid: "Golden split (minor left)"
    composition:
      - elementType: shape
        layer: -1
        bounds: "[0, 0, 486, 720]"
        notes: "Left panel background — full height, primary or surfaceAlt color"
      - elementType: text
        layer: 1
        bounds: "[60, 80, 366, 56]"
        styleRef: "h2"
        notes: "Panel title — left-aligned within panel, 60px left padding from panel edge"
      - elementType: text
        layer: 1
        bounds: "[60, 156, 366, 120]"
        styleRef: "body"
        notes: "Panel subtitle or description — below title, 20px gap"
      - elementType: text
        layer: 1
        bounds: "[526, 80, 694, 560]"
        styleRef: "body"
        notes: "Right-side body content — starts at x=526 (40px gutter from panel edge), full height minus margins"
      - elementType: shape
        layer: 2
        bounds: "[60, 146, 48, 3]"
        notes: "Accent line under panel title — primary color, left-aligned with title"
    alignment_rules:
      - "Left panel content is flush-left at x=60 (panel margin)"
      - "Right content starts at x=526, leaving 40px breathing gutter between panel and body"
      - "Title baseline aligns with right content top at y=80"
    breathing: "40px gutter between panel and body. 60px top margin on both sides. Panel content never extends below y=640."

  three-card-grid:
    description: "Three equal cards arranged horizontally. Each card has a number/icon, title, and 2-3 lines of description. Used for feature lists, process steps, and comparisons."
    grid: "3-col, equal width"
    composition:
      - elementType: text
        layer: 2
        bounds: "[60, 60, 1160, 48]"
        styleRef: "h2"
        notes: "Page title — full width, top-aligned"
      - elementType: shape
        layer: 0
        bounds: "[60, 140, 360, 520]"
        notes: "Card 1 background — fill: card-bg, border: 1px border color, radius per style"
      - elementType: text
        layer: 1
        bounds: "[84, 164, 312, 472]"
        notes: "Card 1 content — 24px internal padding. Stack: number/icon (64px) → title (h3) → 16px gap → description (body)"
      - elementType: shape
        layer: 0
        bounds: "[460, 140, 360, 520]"
        notes: "Card 2 background — 40px gutter from card 1"
      - elementType: text
        layer: 1
        bounds: "[484, 164, 312, 472]"
        notes: "Card 2 content — same internal padding"
      - elementType: shape
        layer: 0
        bounds: "[860, 140, 360, 520]"
        notes: "Card 3 background — 40px gutter from card 2"
      - elementType: text
        layer: 1
        bounds: "[884, 164, 312, 472]"
        notes: "Card 3 content — same internal padding"
      - elementType: shape
        layer: 2
        bounds: "[60, 214, 360, 3]"
        notes: "Card 1 top accent line — primary color, 3px height, spans card width"
    alignment_rules:
      - "All three cards share identical height (520px) and top alignment (y=140)"
      - "Card internal padding is 24px on all sides (content bounds = card bounds + 24px)"
      - "Gutter between cards is exactly 40px (460-60-360=40, 860-460-360=40)"
      - "Card top accent lines align with each other at y=214 (24px below card top)"
    breathing: "60px top margin before title. 60px bottom margin after cards (140+520=660, leaving 60px). Cards feel substantial with 520px height."

  data-dashboard:
    description: "Left 55% is a chart, table, or data visualization. Right 45% has 2-3 large stat callouts with numerals. Used for data-heavy and metrics pages."
    grid: "Asymmetric 55/45 split"
    composition:
      - elementType: text
        layer: 2
        bounds: "[60, 60, 1160, 48]"
        styleRef: "h2"
        notes: "Page title — full width, top-aligned"
      - elementType: chart | table
        layer: 1
        bounds: "[60, 140, 620, 520]"
        notes: "Primary chart or table — left 55%, full body height"
      - elementType: shape
        layer: 0
        bounds: "[60, 140, 620, 520]"
        notes: "Chart background card — subtle surface behind chart, 1px border"
      - elementType: text
        layer: 1
        bounds: "[720, 140, 500, 140]"
        notes: "Stat callout 1 — large numeral (stat-value style) + label (stat-label style) stacked"
      - elementType: text
        layer: 1
        bounds: "[720, 320, 500, 140]"
        notes: "Stat callout 2 — vertically centered in right column, 40px gap from callout 1"
      - elementType: text
        layer: 1
        bounds: "[720, 500, 500, 140]"
        notes: "Stat callout 3 (optional) — bottom of right column"
      - elementType: shape
        layer: 2
        bounds: "[720, 284, 48, 3]"
        notes: "Accent line under stat 1 numeral — primary color"
      - elementType: shape
        layer: 2
        bounds: "[720, 464, 48, 3]"
        notes: "Accent line under stat 2 numeral — primary color"
    alignment_rules:
      - "Chart and stats share top alignment at y=140"
      - "Chart width (620px) + gap (40px) + stats width (500px) = 1160px content width"
      - "Each stat callout is 140px tall with 40px gap between them (140+40+140+40+140=500, fitting in 520px body)"
      - "Stat numerals are left-aligned at x=720 with accent lines directly beneath"
    breathing: "40px gap between chart and stats. Stats have 40px vertical spacing between callouts. Chart has breathing room with 520px height."

  timeline-vertical:
    description: "Vertical timeline with nodes alternating left and right. Each node has a step number, title, and brief description. Used for sequences, roadmaps, and step-by-step processes."
    grid: "Centered spine with alternating wings"
    composition:
      - elementType: text
        layer: 2
        bounds: "[60, 60, 1160, 48]"
        styleRef: "h2"
        notes: "Page title — full width, top-aligned"
      - elementType: shape
        layer: 0
        bounds: "[638, 140, 4, 520]"
        notes: "Central vertical line — 4px wide, primary color or border color, full body height"
      - elementType: shape
        layer: 1
        bounds: "[626, 156, 28, 28]"
        notes: "Step 1 node — centered on line (x=626, 28px diameter), filled circle, primary color"
      - elementType: shape
        layer: 0
        bounds: "[60, 156, 536, 100]"
        notes: "Step 1 card — left side, 40px gap from center line (638-40-536=62, round to 60)"
      - elementType: text
        layer: 1
        bounds: "[84, 172, 488, 68]"
        notes: "Step 1 content — 24px padding inside card. Title (h3) + 8px gap + brief (body-sm)"
      - elementType: shape
        layer: 1
        bounds: "[626, 296, 28, 28]"
        notes: "Step 2 node — 140px below step 1 node (156+28+40+28=252... adjust to 296 for 4 steps)"
      - elementType: shape
        layer: 0
        bounds: "[684, 296, 536, 100]"
        notes: "Step 2 card — right side, 40px gap from center line (638+4+40=682, round to 684)"
      - elementType: text
        layer: 1
        bounds: "[708, 312, 488, 68]"
        notes: "Step 2 content — 24px padding inside card"
      - elementType: shape
        layer: 1
        bounds: "[626, 436, 28, 28]"
        notes: "Step 3 node"
      - elementType: shape
        layer: 0
        bounds: "[60, 436, 536, 100]"
        notes: "Step 3 card — left side"
      - elementType: text
        layer: 1
        bounds: "[84, 452, 488, 68]"
        notes: "Step 3 content"
      - elementType: shape
        layer: 1
        bounds: "[626, 576, 28, 28]"
        notes: "Step 4 node"
      - elementType: shape
        layer: 0
        bounds: "[684, 576, 536, 100]"
        notes: "Step 4 card — right side"
      - elementType: text
        layer: 1
        bounds: "[708, 592, 488, 68]"
        notes: "Step 4 content"
    alignment_rules:
      - "Central line is at x=640 (center of 1280px canvas), rendered as 4px wide bar at x=638"
      - "Nodes are 28px diameter circles centered on the line"
      - "Left cards end at x=596 (638-40-2=596), right cards start at x=684 (638+4+40=682, round to 684)"
      - "Cards on alternating sides create visual rhythm; all cards share identical height (100px)"
      - "Vertical spacing between nodes: 140px (156→296→436→576) for 4 steps in 520px body"
    breathing: "40px gap between center line and card edges. 140px vertical spacing between steps. Cards are compact (100px) to fit 4 steps comfortably."

  standard-content:
    description: "Title at top, body content below, optional sidebar or accent panel. The fallback layout for conceptual and analytical content."
    grid: "1-col primary + optional right sidebar"
    composition:
      - elementType: text
        layer: 2
        bounds: "[60, 60, 1160, 32]"
        styleRef: "label"
        notes: "Eyebrow label — uppercase, primary color, 12px, positioned at top-left"
      - elementType: text
        layer: 1
        bounds: "[60, 100, 700, 56]"
        styleRef: "h2"
        notes: "Page title — left-aligned, 60px from left edge, 40px below eyebrow"
      - elementType: shape
        layer: 2
        bounds: "[60, 168, 48, 3]"
        notes: "Accent line under title — primary color, 48×3px, 2px radius, left-aligned with title"
      - elementType: text
        layer: 1
        bounds: "[60, 200, 700, 460]"
        styleRef: "body"
        notes: "Body content — main area, 60px left margin, extends to bottom at y=660"
      - elementType: shape
        layer: 0
        bounds: "[800, 200, 420, 460]"
        notes: "Optional sidebar card — right side, 40px gap from body (60+700+40=800), same height as body"
      - elementType: text
        layer: 1
        bounds: "[824, 224, 372, 60]"
        styleRef: "h3"
        notes: "Sidebar title — inside card, 24px padding"
      - elementType: text
        layer: 1
        bounds: "[824, 300, 372, 336]"
        styleRef: "body-sm"
        notes: "Sidebar content — below title, fills remaining card space"
    alignment_rules:
      - "Eyebrow, title, accent line, and body are left-aligned at x=60"
      - "Body width is 700px; sidebar starts at x=800 with 40px gap"
      - "Title baseline at y=156 (100+56), accent line at y=168 (12px below title baseline)"
      - "Body starts at y=200 (32px below accent line), extends to y=660"
      - "Sidebar card matches body height (460px) and top alignment (y=200)"
      - "When no sidebar is needed, body expands to full width: [60, 200, 1160, 460]"
    breathing: "12px between eyebrow and title. 12px between title baseline and accent line. 32px between accent line and body. 40px between body and sidebar. Generous vertical rhythm throughout."
"""


def get_decoration_grammar(bucket: str) -> str:
    """Return the decoration-grammar section customized per bucket."""

    if bucket == "editorial":
        style_specific = """    - "Oversized serif drop-cap numeral at 0.10–0.14 opacity behind section titles"
    - "Thin elegant rule (1–2px) in the accent color as a horizontal divider or margin line"
    - "Subtle texture overlay (grain or linen) at 0.03–0.06 opacity on featured surfaces"
    - "Masthead ornament: small geometric mark (diamond, circle, or cross) centered above the eyebrow"
    - "Pull-quote left border: 3–4px solid accent color with generous left padding"""

    elif bucket == "bold":
        style_specific = """    - "45° diagonal hatch or geometric line overlay on accent-colored regions (opacity 0.06)"
    - "Oversized decorative numeral at 0.12 opacity behind titles or stat callouts"
    - "Thick accent border (4–5px) on cards, sidebars, or panel edges"
    - "Hard-edge color block in a corner or edge as a compositional anchor"
    - "Geometric accent shape (triangle, rectangle, circle) at high contrast near the headline"""

    elif bucket == "playful":
        style_specific = """    - "One organic blob frame per slide in an unused corner (asymmetric border-radius, 3px stroke)"
    - "One 2px-stroke scribble per slide (squiggle, star, circle, or arrow) in a margin"
    - "Ghost-blob wallpaper at 0.08 opacity on 1 in 3 slides, anchored to a corner"
    - "Small doodle circle or slightly rotated rectangle (5–10°) as a corner accent"
    - "Double-stroke offset border on the primary card as the signature depth treatment"""

    elif bucket == "retro":
        style_specific = """    - "L-shaped pixel corner brackets (4px stroke, neon or accent color) framing cards or regions"
    - "CRT scanline overlay on dark backgrounds (0.04 opacity)"
    - "Pixel-grid background pattern (40px grid, 0.07 opacity) on dark or colored surfaces"
    - "Vintage texture overlay (grain, vignette, or noise) at 0.03–0.05 opacity"
    - "Small pixel-particle or starfield squares in unused margins (1–2px, low opacity)"""

    else:  # professional
        style_specific = """    - "Thin accent line (1–2px) under titles or as a section divider in the primary accent color"
    - "Subtle gradient overlay (light-to-transparent) on cards or panels for gentle depth"
    - "Minimal geometric shape (circle, square, or line) in a corner at low opacity"
    - "Small icon or glyph mark near the eyebrow label as a navigational hint"
    - "Structured card grid with consistent spacing and alignment as the primary decorative rhythm"""

    return f"""decoration-grammar:
  count-per-slide: "1–3 decorations maximum"
  placement:
    - "Place in corners or edges that the primary content does not occupy"
    - "Offset 20–40px from canvas edges"
    - "Never place over text or in the center of the slide"
  size-range: "30–80px in the largest dimension"
  density:
    cover: "2–3 decorations"
    chapter: "2–3 decorations"
    content: "1–2 decorations"
    final: "1–2 decorations"
  style-specific:
{style_specific}
"""


def process_file(design_md_path: Path, style_name: str) -> bool:
    """Read a design.md, append the new sections, and write back. Returns True if modified."""
    original_text = design_md_path.read_text(encoding="utf-8")

    # Determine bucket
    bucket = get_bucket(style_name)

    # Build the new content to append
    layouts_section = LAYOUTS_SECTION.strip("\n")
    decoration_section = get_decoration_grammar(bucket).strip("\n")

    # Check if already has layouts: or decoration-grammar: at start of line
    has_layouts = any(line.strip().startswith("layouts:") for line in original_text.splitlines())
    has_decoration = any(line.strip().startswith("decoration-grammar:") for line in original_text.splitlines())
    if has_layouts and has_decoration:
        print(f"  SKIP (already has layouts+decoration-grammar): {style_name}")
        return False

    # If only one exists, merge carefully
    if has_layouts and not has_decoration:
        # Append decoration only
        new_text = original_text.rstrip("\n") + "\n\n" + decoration_section + "\n"
    elif has_decoration and not has_layouts:
        # Find decoration-grammar: and insert layouts before it
        insert_pos = original_text.find("decoration-grammar:")
        new_text = (original_text[:insert_pos].rstrip("\n") + "\n\n" +
                    layouts_section + "\n\n" +
                    original_text[insert_pos:])
    else:
        # Neither exists — append both
        new_text = original_text.rstrip("\n") + "\n\n" + layouts_section + "\n\n" + decoration_section + "\n"

    design_md_path.write_text(new_text, encoding="utf-8")
    print(f"  OK [{bucket}]: {style_name}")
    return True


def main():
    modified = 0
    skipped = 0

    # Find all design.md files
    design_files = sorted(STYLES_DIR.glob("*/design.md"))
    print(f"Found {len(design_files)} design.md files\n")

    for design_md in design_files:
        style_name = design_md.parent.name
        if process_file(design_md, style_name):
            modified += 1
        else:
            skipped += 1

    print(f"\nDone: {modified} modified, {skipped} skipped")


if __name__ == "__main__":
    main()
