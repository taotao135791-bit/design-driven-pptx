#!/usr/bin/env python3
"""Batch-update all styles/*/design.md to replace SVG decorations with programmatic draw instructions."""

import os
import re
from pathlib import Path

STYLES_DIR = Path(__file__).resolve().parent.parent / "styles"

# Pre-defined replacement blocks for each style that has SVG file references.
REPLACEMENTS = {
    "8-bit-orbit": """decorations:
  cover-bg:
    draw: "Compose from solid dark-void regions + neon-cyan accent lines + scattered small neon-pink squares. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Corner pixel brackets from small neon-cyan rectangles + center neon-pink cross shape."
    type: "accent"
    color: "#5EDCF4"
  divider:
    draw: "Horizontal line made of small neon-cyan squares (pixel-dash effect) with neon-pink center accent."
    type: "divider"
    color: "#5EDCF4"
  pattern-starfield:
    draw: "Scattered tiny neon-yellow and neon-cyan rectangles (1-2px) and small crosses across the region at low opacity."
    type: "pattern"
    color: "#F4D03F"
    opacity: 0.25
    density: "sparse"
""",
    "biennale-yellow": """decorations:
  cover-bg:
    draw: "Compose from layered sun and sun-soft color blocks + subtle haze gradient overlays. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Large soft sun circle (ellipse) partially off-canvas + thin haze line beneath title."
    type: "accent"
    color: "#F1EE2E"
  divider:
    draw: "Horizontal line with center sun dot: two paper-deep lines on sides + small sun circle in center."
    type: "divider"
    color: "#F1EE2E"
""",
    "block-frame": """decorations:
  cover-bg:
    draw: "Compose from bold black and offwhite blocks + pink and blue accent rectangles arranged in grid-like segments. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Thick black corner brackets from rect shapes + pink inner line + blue dot accent."
    type: "accent"
    color: "#FE90E8"
  divider:
    draw: "Horizontal black line (3px) with pink center rectangle (8px wide)."
    type: "divider"
    color: "#000000"
    accentColor: "#FE90E8"
""",
    "blue-professional": """decorations:
  cover-bg:
    draw: "Compose from soft bg gradient blocks + primary blue geometric lines + subtle text watermark at low opacity. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Corner brackets from thin primary-blue lines + center vertical accent bar."
    type: "accent"
    color: "#1e2bfa"
  divider:
    draw: "Horizontal primary-blue line with small center diamond (rotated square)."
    type: "divider"
    color: "#1e2bfa"
""",
    "bold-poster": """decorations:
  cover-bg:
    draw: "Compose from large red and dark diagonal color blocks + cream text watermark. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Thick red corner brackets from rect shapes + cream inner border line."
    type: "accent"
    color: "#D8000F"
  divider:
    draw: "Bold horizontal red line (4px) with small dark circle center."
    type: "divider"
    color: "#D8000F"
""",
    "broadside": """decorations:
  cover-bg:
    draw: "Compose from cream base + fire-orange horizontal bars + ink-black typographic watermark. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Corner brackets from fire-orange rectangles + center thin fire-orange rule."
    type: "accent"
    color: "#E85D26"
  divider:
    draw: "Horizontal fire-orange line (3px) with ink-black center dash."
    type: "divider"
    color: "#E85D26"
""",
    "capsule": """decorations:
  cover-bg:
    draw: "Compose from cream base + coral capsule-shaped rounded rectangles + ink outline strokes. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Large coral rounded rectangle frame (capsule shape) with white inner stroke."
    type: "accent"
    color: "#E85D4E"
  divider:
    draw: "Horizontal coral line with small white pill/capsule shape in center."
    type: "divider"
    color: "#E85D4E"
""",
    "coral": """decorations:
  pattern-hatch:
    draw: "Multiple thin rotated rectangles (shapeName: rect, rotation: 45, height: 2, opacity: 0.06) tiled across coral regions. Spacing ~20px between lines."
    type: "pattern"
    color: "#000000"
    opacity: 0.06
    spacing: 20
    lineWidth: 2
    angle: 45
  cover-bg:
    draw: "Compose from solid coral top-section + cream bottom-section + zigzag freeform line + accent rules + oversized decorative circles (low opacity). No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Corner brackets from coral rect shapes + center horizontal line + decorative coral dots."
    type: "accent"
    color: "#E85D5D"
  divider:
    draw: "Horizontal ink-black line with coral center dot: two black rect lines on sides + small coral circle in center."
    type: "divider"
    color: "#1A1A1A"
    accentColor: "#E85D5D"
""",
    "cartesian": """decorations:
  cover-bg:
    draw: "Compose from bg-primary and bg-secondary rectangular panels + thin accent grid lines. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Corner brackets from thin accent-colored lines + center crosshair lines."
    type: "accent"
    color: "#8A8178"
  divider:
    draw: "Horizontal accent line with small center square."
    type: "divider"
    color: "#8A8178"
  pattern-grid:
    draw: "Thin accent-colored horizontal and vertical lines (1px, opacity: 0.15) forming a regular grid. Spacing ~40px."
    type: "pattern"
    color: "#8A8178"
    opacity: 0.15
    spacing: 40
    lineWidth: 1
""",
    "cobalt-grid": """decorations:
  cover-bg:
    draw: "Compose from paper and paper-2 blocks + bold ink-blue rectangular bars + grid line overlay. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Corner brackets from ink-blue rect lines + center cobalt dot."
    type: "accent"
    color: "#1F2BE0"
  divider:
    draw: "Horizontal ink-blue line with small paper circle center."
    type: "divider"
    color: "#1F2BE0"
  pattern-grid:
    draw: "Thin ink-blue horizontal and vertical lines (1px, opacity: 0.10) forming a grid. Spacing ~48px."
    type: "pattern"
    color: "#1F2BE0"
    opacity: 0.10
    spacing: 48
    lineWidth: 1
""",
    "creative-mode": """decorations:
  cover-bg:
    draw: "Compose from cream and cream-2 layered blocks + green accent geometric shapes + ink text watermark. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Corner brackets from green lines + ink inner accent."
    type: "accent"
    color: "#1F8A4C"
  divider:
    draw: "Horizontal green line with small ink circle center."
    type: "divider"
    color: "#1F8A4C"
""",
    "daisy-days": """decorations:
  cover-bg:
    draw: "Compose from cream base + soft daisy shapes (yellow circles with white petals drawn as small rects/ellipses) + turquoise accent bands. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Soft-pink rounded petal shapes arranged as corner flowers + butter center dot."
    type: "accent"
    color: "#F7C8D4"
  divider:
    draw: "Horizontal turquoise line with small butter daisy shape in center."
    type: "divider"
    color: "#7ECDC0"
  pattern-dots:
    draw: "Small soft-pink and butter circles (diameter 4-6px, opacity: 0.25) arranged in a regular dot grid. Spacing ~24px."
    type: "pattern"
    color: "#F7C8D4"
    opacity: 0.25
    spacing: 24
    dotSize: 5
""",
    "editorial-forest": """decorations:
  cover-bg:
    draw: "Compose from green-deep base + green-lite leaf shapes (custom freeform paths) + pink flower accents. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Corner brackets from green-lite lines + pink center bud (small ellipse)."
    type: "accent"
    color: "#3a5a36"
  divider:
    draw: "Horizontal green-lite line with small pink center leaf shape."
    type: "divider"
    color: "#3a5a36"
""",
    "editorial-tri-tone": """decorations:
  cover-bg:
    draw: "Compose from pink, butter, and burgundy diagonal or vertical color bands + subtle geometric overlays. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Corner brackets from burgundy lines + butter inner line + pink center dot."
    type: "accent"
    color: "#7A1F35"
  divider:
    draw: "Horizontal burgundy line with butter center dash."
    type: "divider"
    color: "#7A1F35"
""",
    "emerald-editorial": """decorations:
  cover-bg:
    draw: "Compose from bg/b-2/b-3 emerald gradient blocks + ink-blue geometric lines + decorative text watermark. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Corner brackets from ink-blue lines + emerald center dot."
    type: "accent"
    color: "#0F1A5C"
  divider:
    draw: "Horizontal ink-blue line with emerald center square."
    type: "divider"
    color: "#0F1A5C"
""",
    "grove": """decorations:
  cover-bg:
    draw: "Compose from dark green base + lighter green organic shapes (leaf-like freeform paths) + cream text watermark. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Corner brackets from fg-colored lines on dark bg, or green lines on light bg + center dot."
    type: "accent"
    color: "#d4cfbf"
  divider:
    draw: "Horizontal fg line with small green center leaf shape."
    type: "divider"
    color: "#d4cfbf"
""",
    "long-table": """decorations:
  cover-bg:
    draw: "Compose from paper to paper-d gradient blocks + ink-red accent lines + subtle table-row lines. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Corner brackets from ink-red lines + paper center line."
    type: "accent"
    color: "#B53D2A"
  divider:
    draw: "Horizontal ink-red line with small paper circle center."
    type: "divider"
    color: "#B53D2A"
  pattern-dots:
    draw: "Small ink-red circles (diameter 3px, opacity: 0.20) in a regular dot grid. Spacing ~32px."
    type: "pattern"
    color: "#B53D2A"
    opacity: 0.20
    spacing: 32
    dotSize: 3
""",
    "mat": """decorations:
  cover-bg:
    draw: "Compose from dark green base + cream geometric weave pattern (overlapping horizontal and vertical thin rectangles) + accent lines. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Corner brackets from cream lines on dark bg, or dark lines on cream bg + center dash."
    type: "accent"
    color: "#F0E8D2"
  divider:
    draw: "Horizontal cream line with small dark center square."
    type: "divider"
    color: "#F0E8D2"
""",
    "monochrome": """decorations:
  cover-bg:
    draw: "Compose from cream-paper base + ink-black geometric blocks + subtle typographic watermark at low opacity. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Corner brackets from ink-black lines + cream-warm inner line."
    type: "accent"
    color: "#1A1A16"
  divider:
    draw: "Horizontal ink-black line (2px) with cream-paper center dash."
    type: "divider"
    color: "#1A1A16"
""",
    "neo-grid-bold": """decorations:
  cover-bg:
    draw: "Compose from paper and bg blocks + bold accent-lemon rectangular bars + ink grid lines. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Thick accent-lemon corner brackets + ink inner border."
    type: "accent"
    color: "#E6FF3D"
  divider:
    draw: "Bold horizontal ink line with accent-lemon center square."
    type: "divider"
    color: "#0A0A0A"
    accentColor: "#E6FF3D"
  pattern-grid:
    draw: "Thin muted horizontal and vertical lines (1px, opacity: 0.12) forming a grid. Spacing ~56px."
    type: "pattern"
    color: "#8A8A85"
    opacity: 0.12
    spacing: 56
    lineWidth: 1
""",
    "peoples-platform": """decorations:
  cover-bg:
    draw: "Compose from blue and blue-deep blocks + orange diagonal bars + red accent shapes + subtle grain texture from tiny dots. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Corner brackets from orange lines + blue center dot."
    type: "accent"
    color: "#F2A03A"
  divider:
    draw: "Horizontal orange line with red center circle."
    type: "divider"
    color: "#F2A03A"
  pattern-grain:
    draw: "Scattered tiny blue and orange rectangles (1-2px, opacity: 0.15) creating a noise texture."
    type: "pattern"
    color: "#2C2CDC"
    opacity: 0.15
    density: "dense"
""",
    "pin-and-paper": """decorations:
  cover-bg:
    draw: "Compose from yellow paper base + cream and paper-2 layered blocks + subtle pin-hole dots. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Corner brackets from dark brown lines (derived from paper tones) + red pin dot center."
    type: "accent"
    color: "#E8D85A"
  divider:
    draw: "Horizontal brown line with yellow center dash."
    type: "divider"
    color: "#8B7355"
  pattern-grain:
    draw: "Scattered tiny brown dots and short lines (opacity: 0.12) simulating paper grain."
    type: "pattern"
    color: "#8B7355"
    opacity: 0.12
    density: "medium"
""",
    "pink-script": """decorations:
  cover-bg:
    draw: "Compose from paper-blush base + ink-deep and ink-violet gradient panels + pink script-like swash lines (freeform curves). No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Elegant pink swash curves (freeform paths) + ink-deep corner flourishes."
    type: "accent"
    color: "#ED3D8C"
  divider:
    draw: "Horizontal pink line with small ink-deep heart or dot center."
    type: "divider"
    color: "#ED3D8C"
  pattern-grain:
    draw: "Scattered tiny ink-violet dots (opacity: 0.08) across blush background."
    type: "pattern"
    color: "#0F0D11"
    opacity: 0.08
    density: "sparse"
""",
    "playful": """decorations:
  cover-bg:
    draw: "Compose from bg and bg-alt rounded color blobs + light accent shapes + playful scattered dots. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Corner brackets from text-colored lines + bg center circle."
    type: "accent"
    color: "#1A1A1A"
  divider:
    draw: "Horizontal text-colored line with bg-alt center dot."
    type: "divider"
    color: "#1A1A1A"
  pattern-dots:
    draw: "Small light and bg-alt circles (diameter 6px, opacity: 0.30) in a playful irregular dot grid. Spacing ~28px."
    type: "pattern"
    color: "#F7DEC6"
    opacity: 0.30
    spacing: 28
    dotSize: 6
""",
    "raw-grid": """decorations:
  cover-bg:
    draw: "Compose from black and white bold blocks + pink and green accent rectangles in raw grid arrangement. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Thick black corner brackets + pink inner line + green dot accent."
    type: "accent"
    color: "#000000"
  divider:
    draw: "Horizontal black line (3px) with pink center rectangle."
    type: "divider"
    color: "#000000"
    accentColor: "#F2D4CF"
  pattern-grid:
    draw: "Thin gray horizontal and vertical lines (1px, opacity: 0.15) forming a regular grid. Spacing ~40px."
    type: "pattern"
    color: "#F5F5F5"
    opacity: 0.15
    spacing: 40
    lineWidth: 1
""",
    "retro-windows": """decorations:
  cover-bg:
    draw: "Compose from bg-gray and bg-light blocks + white and black beveled window frames (overlapping rects with offsets) + title-bar accents. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Beveled corner frame from gray, white, and dark rects simulating 3D window border."
    type: "accent"
    color: "#c0c0c0"
  divider:
    draw: "Horizontal gray line with inset shadow effect (overlapping light and dark rects)."
    type: "divider"
    color: "#808080"
""",
    "retro-zine": """decorations:
  cover-bg:
    draw: "Compose from bg and bg-dark textured blocks + green ransom-note style rect patches + black ink splatter shapes (irregular freeform blobs). No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Rough black corner brackets (slightly irregular rects) + green center accent."
    type: "accent"
    color: "#1A1A1A"
  divider:
    draw: "Dashed horizontal black line with green center square."
    type: "divider"
    color: "#1A1A1A"
  pattern-grain:
    draw: "Scattered tiny black dots and short lines (opacity: 0.15) creating zine photocopy grain."
    type: "pattern"
    color: "#1A1A1A"
    opacity: 0.15
    density: "medium"
""",
    "sakura-chroma": """decorations:
  cover-bg:
    draw: "Compose from paper and paper-dk blocks + red and pink cherry-petal shapes (small ellipses with slight rotation) + ink accent lines. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Corner brackets from ink lines + pink petal center accents."
    type: "accent"
    color: "#3A2516"
  divider:
    draw: "Horizontal ink line with red center petal shape."
    type: "divider"
    color: "#3A2516"
  pattern-dots:
    draw: "Small red and pink circles (diameter 4px, opacity: 0.20) in a regular dot grid. Spacing ~24px."
    type: "pattern"
    color: "#E5392A"
    opacity: 0.20
    spacing: 24
    dotSize: 4
""",
    "scatterbrain": """decorations:
  cover-bg:
    draw: "Compose from yellow, blue, and pink diagonal or scattered color blocks + playful scribble lines (freeform). No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Corner brackets from yellow-deep lines + blue center dot + pink accent."
    type: "accent"
    color: "#ffd43b"
  divider:
    draw: "Wavy horizontal line (freeform) with alternating color dashes."
    type: "divider"
    color: "#ffe066"
  pattern-dots:
    draw: "Scattered small yellow, blue, and pink circles (diameter 5-8px, opacity: 0.30) in playful random layout."
    type: "pattern"
    color: "#ffe066"
    opacity: 0.30
    spacing: "random"
    dotSize: 6
""",
    "signal": """decorations:
  cover-bg:
    draw: "Compose from navy and navy-alt blocks + cream geometric bars + signal-wave freeform curves. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Corner brackets from cream lines on navy bg + center signal dot."
    type: "accent"
    color: "#F0ECE3"
  divider:
    draw: "Horizontal cream line with small navy center circle."
    type: "divider"
    color: "#F0ECE3"
  pattern-grid:
    draw: "Thin cream horizontal and vertical lines (1px, opacity: 0.10) forming a grid. Spacing ~48px."
    type: "pattern"
    color: "#F0ECE3"
    opacity: 0.10
    spacing: 48
    lineWidth: 1
""",
    "soft-editorial": """decorations:
  cover-bg:
    draw: "Compose from paper and paper-2 soft blocks + ink and pink accent curves + subtle watercolor-like overlays (low-opacity rounded rects). No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Soft pink curved corner brackets (rounded rects) + ink center line."
    type: "accent"
    color: "#E1A4C2"
  divider:
    draw: "Horizontal ink line (2px) with pink center dot."
    type: "divider"
    color: "#2A241B"
""",
    "stencil-tablet": """decorations:
  cover-bg:
    draw: "Compose from bone and paper blocks + black stencil-like geometric cutouts (sharp-angled freeform paths) + sienna accent lines. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Corner brackets from black sharp-angled paths (stencil style) + sienna center dash."
    type: "accent"
    color: "#000000"
  divider:
    draw: "Horizontal black line with sienna center diamond."
    type: "divider"
    color: "#000000"
""",
    "studio": """decorations:
  cover-bg:
    draw: "Compose from near-black base + acid-yellow bold geometric bars + near-black-alt grid lines + subtle text watermark. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Thick acid-yellow corner brackets + near-black inner border."
    type: "accent"
    color: "#F5D200"
  divider:
    draw: "Horizontal acid-yellow line (3px) with near-black center square."
    type: "divider"
    color: "#F5D200"
""",
    "vellum": """decorations:
  cover-bg:
    draw: "Compose from navy and navy-alt gradient blocks + yellow accent lines + subtle geometric watermark. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Corner brackets from yellow lines on navy bg + navy-mid center dot."
    type: "accent"
    color: "#E8D85C"
  divider:
    draw: "Horizontal yellow line with navy-deep center circle."
    type: "divider"
    color: "#E8D85C"
""",
}


def replace_decorations(filepath: Path, new_block: str) -> bool:
    """Replace the decorations block in a design.md file. Returns True if modified."""
    content = filepath.read_text(encoding="utf-8")

    # Find the decorations block: starts with ^decorations: and ends at the next top-level key or EOF.
    # We need to handle it carefully so we don't break YAML.
    pattern = re.compile(r"^(decorations:.*?)(?=\n\S|\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(content)
    if not match:
        return False

    old_block = match.group(1)
    # Ensure the new block ends with a single newline so the following section is separated cleanly.
    new_block_stripped = new_block.rstrip("\n") + "\n"
    new_content = content[:match.start()] + new_block_stripped + content[match.end():]

    if new_content == content:
        return False

    filepath.write_text(new_content, encoding="utf-8")
    return True


def main():
    modified = []
    skipped = []

    for style_dir in sorted(STYLES_DIR.iterdir()):
        if not style_dir.is_dir():
            continue
        design_md = style_dir / "design.md"
        if not design_md.exists():
            skipped.append(f"{style_dir.name}: no design.md")
            continue

        style_name = style_dir.name
        new_block = REPLACEMENTS.get(style_name)
        if not new_block:
            skipped.append(f"{style_name}: no replacement defined")
            continue

        if replace_decorations(design_md, new_block):
            modified.append(style_name)
        else:
            skipped.append(f"{style_name}: no decorations block found")

    print("MODIFIED:")
    for m in modified:
        print(f"  - {m}")
    print(f"\nTOTAL MODIFIED: {len(modified)}")
    print("\nSKIPPED:")
    for s in skipped:
        print(f"  - {s}")


if __name__ == "__main__":
    main()
