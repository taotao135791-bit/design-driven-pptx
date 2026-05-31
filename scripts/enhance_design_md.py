#!/usr/bin/env python3
"""
Enhance all styles/*/design.md files by appending `layouts:` and `decoration-grammar:` sections.
"""

import os
from pathlib import Path

# Base directory
STYLES_DIR = Path("/Users/guolintao/Downloads/Kimi_Agent_PPT%E7%94%9F%E6%88%90%E6%8A%80%E8%83%BD%E5%8C%96-2/design-driven-pptx/styles")

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


# Universal layouts section (identical for all styles)
LAYOUTS_SECTION = """
layouts:
  full-statement:
    description: "One dominant statement or conclusion fills the center of the slide. Eyebrow label above, decorative numeral or mark behind at low opacity. Used for key conclusions and manifesto moments."
    composition:
      - elementType: shape | text
        layer: -1
        notes: "Background color block or decorative numeral at low opacity"
      - elementType: text
        layer: 2
        notes: "Eyebrow label (sectionLabel style)"
      - elementType: text
        layer: 1
        notes: "Large display statement (heroTitle or sectionHeadline style), 50-70% width, vertically centered"
      - elementType: shape
        layer: 2
        notes: "Small accent line or shape near the statement"
  asymmetric-split:
    description: "Left 35-40% is a colored/surfaced panel with title and subtitle. Right 60-65% is body content on default background. Used for topic overviews and chapter introductions."
    composition:
      - elementType: shape
        layer: -1
        notes: "Left panel background color block, 35-45% width, full height"
      - elementType: text
        layer: 1
        notes: "Panel title (sectionHeadline), left-aligned within panel"
      - elementType: text
        layer: 1
        notes: "Panel subtitle or description (body style)"
      - elementType: text
        layer: 1
        notes: "Right-side body content (body style)"
  three-card-grid:
    description: "Three equal cards arranged horizontally. Each card has a number/icon, title, and 2-3 lines of description. Used for feature lists, process steps, and comparisons."
    composition:
      - elementType: shape
        layer: 0
        notes: "Card 1 background (3 per row), evenly spaced"
      - elementType: text
        layer: 1
        notes: "Card 1 content: number/icon + title + description"
      - elementType: shape
        layer: 0
        notes: "Card 2 background"
      - elementType: text
        layer: 1
        notes: "Card 2 content"
      - elementType: shape
        layer: 0
        notes: "Card 3 background"
      - elementType: text
        layer: 1
        notes: "Card 3 content"
  data-dashboard:
    description: "Left half is a chart, table, or data visualization. Right half has 2-3 large stat callouts with numerals. Used for data-heavy and metrics pages."
    composition:
      - elementType: chart | table
        layer: 1
        notes: "Chart or table on left half"
      - elementType: text
        layer: 1
        notes: "Stat callout 1: large numeral + label"
      - elementType: text
        layer: 1
        notes: "Stat callout 2: large numeral + label"
      - elementType: text
        layer: 1
        notes: "Optional stat callout 3"
  timeline-vertical:
    description: "Vertical timeline with nodes alternating left and right. Each node has a step number, title, and brief description. Used for sequences, roadmaps, and step-by-step processes."
    composition:
      - elementType: shape
        layer: 0
        notes: "Vertical line or connector"
      - elementType: shape
        layer: 1
        notes: "Step node circles (alternating fill: outlined/filled)"
      - elementType: text
        layer: 1
        notes: "Step title and description (alternating left/right)"
  standard-content:
    description: "Title at top, body content below, optional sidebar or accent panel. The fallback layout for conceptual and analytical content."
    composition:
      - elementType: text
        layer: 2
        notes: "Eyebrow label"
      - elementType: text
        layer: 1
        notes: "Page title (columnTitle style)"
      - elementType: shape
        layer: 2
        notes: "Accent line under title"
      - elementType: text
        layer: 1
        notes: "Body content (body style, multi-paragraph)"
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
    if has_layouts or has_decoration:
        print(f"  SKIP (already has layouts/decoration-grammar): {style_name}")
        return False

    # Append with blank line separation
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
