#!/usr/bin/env python3
"""
Upgrade minimal design.md (117-118 lines) to full design.md (600+ lines).

Parses existing colors/textStyles/tableStyles and generates a complete,
professional-grade design system with:
  - Full frontmatter YAML (colors, typography, spacing, components)
  - Enhanced decoration-grammar
  - Complete Markdown sections (Overview, Colors, Typography, Layout,
    Depth and Elevation, Shapes and Treatment, Do's and Don'ts,
    CJK & International Content)

Usage:
    python upgrade_minimal_designs.py
"""

import re
from pathlib import Path

STYLES_DIR = Path(__file__).resolve().parent.parent / "styles"


def extract_yaml_block(text: str, block_name: str) -> str:
    """Extract a ```yaml ... ``` block by its leading header."""
    pattern = rf"##?\s*{re.escape(block_name)}.*?```yaml\n(.*?)```"
    m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""


def parse_colors(yaml_text: str) -> dict:
    colors = {}
    for line in yaml_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            colors[key.strip()] = val.strip().strip('"').strip("'")
    return colors


def parse_text_styles(yaml_text: str) -> dict:
    styles = {}
    current = None
    for line in yaml_text.splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        # "  heroTitle:" starts a new block
        m = re.match(r"^(\s+)(\w+):\s*$", line)
        if m and len(m.group(1)) <= 4:
            current = m.group(2)
            styles[current] = {}
            continue
        if current and ":" in line:
            key, val = line.split(":", 1)
            styles[current][key.strip()] = val.strip().strip('"').strip("'")
    return styles


def is_dark_theme(colors: dict) -> bool:
    """Heuristic: if background is dark, it's a dark theme."""
    bg = colors.get("background", "#FFFFFF")
    # Simple luminance check
    def lum(hexcol):
        hexcol = hexcol.lstrip("#")
        if len(hexcol) == 3:
            hexcol = "".join(c * 2 for c in hexcol)
        r, g, b = int(hexcol[0:2], 16), int(hexcol[2:4], 16), int(hexcol[4:6], 16)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    return lum(bg) < 128


# ---------------------------------------------------------------------------
# Per-style configuration — the soul of each design system
# ---------------------------------------------------------------------------

STYLE_CONFIG = {
    "apple-demo": {
        "name": "Apple Demo",
        "description": "A dark, tech-minimal presentation system inspired by Apple's product keynotes. Deep charcoal canvas (#121212) with electric cobalt blue (#1E88E5) as the single accent. SF Pro Display carries headlines with generous letter-spacing; SF Pro Text handles body copy with light gray secondary text. The aesthetic is relentlessly minimal — every element earns its place, negative space is the primary compositional tool, and the blue accent appears only in surgical moments: stat numerals, eyebrow labels, and thin divider rules. Built for product launches, technical demos, and any deck that needs to feel like it came from Cupertino.",
        "bucket": "professional",
        "mood": "tech-minimal",
        "dark": True,
        "display_font": "'SF Pro Display', 'Inter', sans-serif",
        "body_font": "'SF Pro Text', 'Inter', sans-serif",
        "cjk_display": "Inter",
        "cjk_body": "Inter",
        "signature_treatments": [
            "Every stat numeral is SF Pro Display in {colors.primary} — the blue data signal is the system's numerical voice",
            "Every eyebrow label is SF Pro Text uppercase with 3-4px letter-spacing in {colors.primary} blue",
            "Thin 1-2px {colors.primary} accent lines under headlines and as section dividers — never thicker than 2px",
            "Cards use subtle surface elevation via translucent borders (rgba(255,255,255,0.08)) — no drop shadows",
            "Body text never appears in pure white on dark surfaces — {colors.text} (#A0A0A0) is the maximum body contrast",
        ],
        "dos": [
            "Use generous negative space — the dark canvas is the primary design element",
            "Set every stat figure in {colors.primary} blue at 56px or larger",
            "Apply 1-2px {colors.primary} lines as the only decorative element",
            "Use {colors.surfaceAlt} (#1E1E1E) for card backgrounds against the darker #121212 canvas",
            "Keep body text in {colors.text} (#A0A0A0) — never brighter than this for paragraphs",
            "Use uppercase eyebrow labels with wide tracking for section openers",
        ],
        "donts": [
            "Don't use drop shadows, glows, or blur effects — depth comes from surface contrast only",
            "Don't introduce a second accent color — cobalt blue is the only chromatic voice",
            "Don't crowd slides with more than 3 content elements — one headline, one body, one visual",
            "Don't use pure white (#FFFFFF) for body paragraphs — it causes eye fatigue on dark backgrounds",
            "Don't use borders thicker than 2px — the system is hairline-precise",
        ],
        "depth": "Flat and surface-based. No shadows. Depth comes from three mechanisms: (1) canvas-to-surface contrast — #121212 canvas vs #1E1E1E card surfaces; (2) border-as-frame — 1px rgba(255,255,255,0.08) borders on cards; (3) accent-line depth — a 2px cobalt line under a headline creates spatial anchoring without lifting the element off the surface.",
        "shapes": "All corners are sharp (0px radius). Cards are strict rectangles. The only soft element is the 2px rounded caps on accent lines (border-radius: 1px). This square-corner discipline is essential to the tech-minimal register.",
        "density": "Sparse and deliberate. Target 3-5 content elements per content slide, 1-3 per statement slide. Padding is generous: 60px page margins, 40px card internal padding.",
    },
    "corporate-blue": {
        "name": "Corporate Blue",
        "description": "A clean, modern corporate presentation system on a light gray canvas (#F5F5F5) with electric blue (#1E88E5) as the single accent. Montserrat carries headlines with confident geometric weight; Open Sans handles body copy with friendly readability. The aesthetic bridges corporate professionalism with contemporary design — structured grids, clear hierarchy, and a blue accent that signals trust and competence. Built for business proposals, quarterly reports, investor decks, and any presentation that needs to project reliability and modernity.",
        "bucket": "professional",
        "mood": "modern",
        "dark": False,
        "display_font": "'Montserrat', 'Noto Sans SC', sans-serif",
        "body_font": "'Open Sans', 'Noto Sans SC', sans-serif",
        "cjk_display": "Noto Sans SC",
        "cjk_body": "Noto Sans SC",
        "signature_treatments": [
            "Every headline is Montserrat with moderate letter-spacing (1px) — the geometric confidence is the system's voice",
            "Every stat numeral is Montserrat in {colors.primary} blue — bold and unmissable",
            "Every eyebrow label is Open Sans uppercase with 4px letter-spacing in {colors.primary}",
            "Cards use white fill (#FFFFFF) with subtle bottom shadow or 1px border for gentle elevation",
            "Accent lines are 2-3px solid {colors.primary} — used under titles and as section dividers",
        ],
        "dos": [
            "Use white cards (#FFFFFF) on the light gray canvas for content grouping",
            "Set stat numerals in bold {colors.primary} at 48-56px for maximum impact",
            "Apply 2-3px {colors.primary} accent lines under section headlines",
            "Use Montserrat for every headline and display moment — its geometric confidence defines the system",
            "Keep body text in {colors.text} (#6B6B6B) for comfortable reading on light surfaces",
            "Use uppercase eyebrow labels with wide tracking (4px) for section navigation",
        ],
        "donts": [
            "Don't use dark backgrounds — the system is built for light surfaces only",
            "Don't use more than one accent color — electric blue is the corporate identity",
            "Don't use script or decorative fonts — Montserrat and Open Sans are the only voices",
            "Don't crowd cards with excessive content — one title, one stat, 2-3 bullet points max per card",
            "Don't use drop shadows heavier than 0 2px 8px rgba(0,0,0,0.08) — elevation must stay subtle",
        ],
        "depth": "Gentle and card-based. Cards use subtle elevation: white fill with either (1) a 1px #E0E0E0 border, or (2) a very soft shadow (0 2px 8px rgba(0,0,0,0.06)). No heavy shadows, no gradients. Depth is created by surface contrast: #F5F5F5 canvas → #FFFFFF card → #1E88E5 accent line.",
        "shapes": "Cards use 8-12px border-radius for a contemporary, approachable feel. Accent lines have 2px rounded caps. Buttons are fully rounded pills. The soft-corner discipline distinguishes this system from stark corporate templates.",
        "density": "Medium. Content slides can hold 4-6 elements comfortably. Grid layouts with 2-3 cards per row are standard. Padding: 48px page margins, 24-32px card internal padding.",
    },
    "playful-pink": {
        "name": "Playful Pink",
        "description": "A vibrant, energetic presentation system on a light gray canvas (#F5F5F5) with hot pink (#EC407A) as the single accent. Poppins carries headlines with rounded geometric warmth; Nunito handles body copy with friendly openness. The aesthetic is youthful, creative, and unapologetically bold — rounded cards, rotated elements, organic blob shapes, and a pink accent that delivers joy and confidence. Built for creative pitches, startup decks, educational content, and any presentation that needs personality and energy.",
        "bucket": "playful",
        "mood": "playful",
        "dark": False,
        "display_font": "'Poppins', 'ZCOOL KuaiLe', sans-serif",
        "body_font": "'Nunito', 'Yozai', sans-serif",
        "cjk_display": "ZCOOL KuaiLe",
        "cjk_body": "Yozai",
        "signature_treatments": [
            "Headlines use Poppins with positive letter-spacing (2-4px) — the rounded warmth is the system's voice",
            "Cards carry slight rotations (±2-3°) and organic asymmetric border-radii — never perfectly rectangular",
            "Every stat numeral is Poppins in {colors.primary} pink at 56px or larger",
            "Organic blob frames in corners with 3px {colors.primary} stroke — the doodle element is signature",
            "Accent elements include scribble lines, small rotated shapes, and scattered decorative dots",
        ],
        "dos": [
            "Rotate cards slightly (±2-3°) for a playful, sticker-sheet feel",
            "Use organic blob shapes with asymmetric border-radius as corner decorations",
            "Set stat numerals in bold {colors.primary} pink — they should feel celebratory",
            "Use hand-drawn-style scribble lines (2px stroke) as dividers and accents",
            "Apply generous internal padding (28-36px) inside cards — breathing room amplifies the playful energy",
            "Use uppercase labels with wide tracking in {colors.primary} for section navigation",
        ],
        "donts": [
            "Don't use sharp 0px corners — rounded, organic shapes are the system's DNA",
            "Don't use more than one accent color — hot pink is the solo chromatic voice",
            "Don't make layouts perfectly symmetrical — intentional asymmetry creates playful rhythm",
            "Don't use heavy shadows or gradients — depth comes from color contrast and rotation, not elevation",
            "Don't use formal serif fonts — Poppins and Nunito's rounded geometry is non-negotiable",
        ],
        "depth": "Flat and color-based. No shadows, no gradients. Depth comes from: (1) rotation — tilted cards create perceived dimensionality; (2) color contrast — pink on light gray is inherently punchy; (3) organic shapes — blobs and scribbles create visual layers without lifting elements off the surface.",
        "shapes": "All shapes are organic and rounded. Cards use asymmetric border-radius (e.g., 24px 8px 24px 8px). Blob frames use irregular curves. Even accent lines have hand-drawn irregularity. Sharp corners and perfect rectangles immediately collapse the playful register.",
        "density": "Medium to dense. Playful slides can hold more elements than minimal systems — 5-7 elements per slide with overlapping and staggered positioning. The energy comes from density and variety, not sparsity.",
    },
    "retro-pixel": {
        "name": "Retro Pixel",
        "description": "A nostalgic, terminal-inspired presentation system on a deep black canvas (#121212) with phosphor green (#43A047) as the single accent. Courier Prime — a monospace typewriter face — carries every text element, creating the unmistakable register of 1980s computing: CRT monitors, green phosphor glow, and 8-bit precision. The aesthetic is retro-technical, pixel-perfect, and unapologetically geeky. Built for technical presentations, developer talks, retro-gaming pitches, and any deck that wants to channel the romance of early computing.",
        "bucket": "retro",
        "mood": "retro",
        "dark": True,
        "display_font": "'Courier Prime', 'ZCOOL XiaoWei', monospace",
        "body_font": "'Courier Prime', 'Yozai', monospace",
        "cjk_display": "ZCOOL XiaoWei",
        "cjk_body": "Yozai",
        "signature_treatments": [
            "Every text element is Courier Prime monospace — the typewriter voice is the system's identity",
            "Phosphor green (#43A047) is the only accent — used for stat numerals, eyebrow labels, and terminal-style prompts",
            "CRT scanline overlay on dark backgrounds at 4% opacity — the retro screen texture",
            "Pixel-grid background pattern (40px grid, 7% opacity) on dark surfaces",
            "L-shaped pixel corner brackets (4px stroke, green) framing cards and content regions",
            "Blinking-cursor-style block at the end of key lines — the terminal metaphor",
        ],
        "dos": [
            "Use Courier Prime for absolutely every text element — headlines, body, labels, stats",
            "Apply CRT scanline overlays on all dark-background slides",
            "Set stat numerals in phosphor green (#43A047) at 48-56px",
            "Use pixel-grid background patterns on content-heavy slides",
            "Frame content regions with L-shaped pixel corner brackets in green",
            "Use terminal-style prompts ('>' or '$') before list items and commands",
        ],
        "donts": [
            "Don't use proportional fonts — Courier Prime monospace is the non-negotiable identity",
            "Don't use more than one accent color — phosphor green is the CRT voice",
            "Don't use rounded corners — everything is pixel-sharp (0px radius)",
            "Don't use gradients or shadows — the system is flat, pixel-perfect, and screen-native",
            "Don't use light backgrounds — the system lives on black, like a CRT monitor in a dark room",
        ],
        "depth": "Flat and screen-native. No shadows, no gradients. Depth comes from: (1) scanline texture — horizontal lines at 4% opacity create the CRT surface feel; (2) pixel-grid pattern — a 40px grid at 7% opacity adds technical precision; (3) corner brackets — L-shaped pixel frames create compositional boundaries without lifting elements.",
        "shapes": "All shapes are pixel-sharp rectangles with 0px radius. Lines are straight and orthogonal. The only curves are in the monospace letterforms themselves. Diagonal elements are forbidden — the system is grid-locked and axis-aligned.",
        "density": "Medium. Terminal-style slides can be text-dense (like a code editor), but statement slides should have generous negative space around a single green phosphor message. Content slides: 4-6 elements. Statement slides: 1-2 elements with massive surrounding void.",
    },
    "tech-neon": {
        "name": "Tech Neon",
        "description": "A bold, futuristic presentation system on a deep black canvas (#121212) with electric teal (#00897B) as the single accent. Bebas Neue — a tall, condensed display face — carries headlines with dramatic vertical presence; Inter handles body copy with clean neutrality. The aesthetic is high-tech, forward-looking, and assertive — tall headlines, precise grids, neon accent lines, and a dark canvas that makes the teal glow. Built for tech startups, AI product launches, innovation reports, and any deck that needs to feel like it's from the future.",
        "bucket": "professional",
        "mood": "tech-minimal",
        "dark": True,
        "display_font": "'Bebas Neue', 'ZCOOL XiaoWei', sans-serif",
        "body_font": "'Inter', 'Yozai', sans-serif",
        "cjk_display": "ZCOOL XiaoWei",
        "cjk_body": "Yozai",
        "signature_treatments": [
            "Headlines are Bebas Neue — tall, condensed, uppercase by default — the dramatic vertical presence is the system's voice",
            "Every stat numeral is Bebas Neue in {colors.primary} teal at 56px or larger",
            "Every eyebrow label is Inter uppercase with 4px letter-spacing in {colors.primary} teal",
            "Neon accent lines: 2px solid {colors.primary} with a subtle glow effect (text-shadow or border-glow)",
            "Dark cards use {colors.surfaceAlt} (#1E1E1E) with 1px rgba(0,137,123,0.3) teal borders",
            "Grid-aligned layouts — everything snaps to an implicit 8px or 40px grid",
        ],
        "dos": [
            "Use Bebas Neue for all headlines and display moments — its tall condensed forms create dramatic vertical rhythm",
            "Apply 2px {colors.primary} teal lines as accent dividers and under headlines",
            "Set stat numerals in {colors.primary} teal — they should feel like glowing data readouts",
            "Use {colors.surfaceAlt} (#1E1E1E) for card backgrounds with subtle teal-tinted borders",
            "Keep body text in {colors.text} (#A0A0A0) — never brighter for paragraphs on dark surfaces",
            "Use uppercase labels with wide tracking in {colors.primary} for section navigation",
        ],
        "donts": [
            "Don't use lowercase in Bebas Neue headlines — the face is designed for uppercase impact",
            "Don't use more than one accent color — electric teal is the futuristic signal",
            "Don't use rounded corners — the system is sharp and precise (0-4px max)",
            "Don't use heavy shadows — depth comes from surface contrast and neon lines, not elevation",
            "Don't use light backgrounds — the dark canvas is essential to the neon glow effect",
        ],
        "depth": "Surface-contrast and neon-line based. No drop shadows. Depth comes from: (1) canvas-to-surface contrast — #121212 canvas vs #1E1E1E cards; (2) neon border glow — 1px borders in rgba(0,137,123,0.3) create the impression of light emission; (3) accent line anchoring — 2px teal lines create spatial boundaries without lifting elements.",
        "shapes": "Sharp and precise. Cards are rectangles with 0-4px radius (prefer 0px for tech edge, 4px for slightly softer moments). Accent lines are perfectly straight. The system rewards geometric precision — every angle is intentional.",
        "density": "Sparse to medium. The tall Bebas Neue headlines demand vertical space, so slides naturally have fewer elements. Target 3-5 elements per content slide. Padding: 56px page margins, 32px card internal padding.",
    },
    "tech-neon-v2": {
        "name": "Tech Neon V2",
        "description": "An evolution of Tech Neon — a bold, futuristic presentation system on a deep black canvas (#121212) with electric teal (#00897B) as the single accent. Bebas Neue carries headlines with dramatic vertical presence; Inter handles body copy with clean neutrality. This variant refines the original with sharper contrast ratios, more precise grid alignment, and enhanced readability for data-dense slides. Built for technical deep-dives, engineering reviews, and data-heavy innovation reports.",
        "bucket": "professional",
        "mood": "tech-minimal",
        "dark": True,
        "display_font": "'Bebas Neue', 'ZCOOL XiaoWei', sans-serif",
        "body_font": "'Inter', 'Yozai', sans-serif",
        "cjk_display": "ZCOOL XiaoWei",
        "cjk_body": "Yozai",
        "signature_treatments": [
            "Headlines are Bebas Neue — tall, condensed, uppercase — dramatic vertical presence",
            "Every stat numeral is Bebas Neue in {colors.primary} teal at 56px or larger",
            "Every eyebrow label is Inter uppercase with 4px letter-spacing in {colors.primary} teal",
            "Neon accent lines: 2px solid {colors.primary} with subtle glow",
            "Dark cards use {colors.surfaceAlt} (#1E1E1E) with 1px rgba(0,137,123,0.3) teal borders",
            "Data-dense grids use alternating row tints in rgba(0,137,123,0.04) for readability",
        ],
        "dos": [
            "Use Bebas Neue for all headlines — its tall condensed forms create dramatic vertical rhythm",
            "Apply 2px {colors.primary} teal accent lines for section dividers",
            "Set stat numerals in {colors.primary} teal for glowing data readout effect",
            "Use alternating row tints in data tables for enhanced scannability",
            "Keep body text in {colors.text} (#A0A0A0) for comfortable dark-mode reading",
            "Use uppercase labels with wide tracking in {colors.primary}",
        ],
        "donts": [
            "Don't use lowercase Bebas Neue — designed for uppercase impact only",
            "Don't use more than one accent color — electric teal only",
            "Don't use rounded corners above 4px — precision is key",
            "Don't use heavy shadows — rely on surface contrast and neon lines",
            "Don't use light backgrounds — dark canvas is essential",
        ],
        "depth": "Surface-contrast and neon-line based. No drop shadows. Depth from canvas-to-surface contrast, teal-tinted borders, and accent line anchoring.",
        "shapes": "Sharp and precise. 0-4px radius maximum. Geometric precision in every element.",
        "density": "Medium to dense. This variant supports more data-dense layouts than V1, with 4-6 elements per content slide while maintaining the system's vertical rhythm.",
    },
}


# ---------------------------------------------------------------------------
# Build helpers
# ---------------------------------------------------------------------------

def build_frontmatter(colors: dict, text_styles: dict, cfg: dict) -> str:
    """Build the YAML frontmatter section."""
    is_dark = cfg["dark"]
    primary = colors.get("primary", "#1E88E5")
    primary_dark = colors.get("primaryDark", primary)
    bg = colors.get("background", "#121212" if is_dark else "#F5F5F5")
    surface = colors.get("surfaceAlt", bg)
    ink = colors.get("ink", "#FFFFFF" if is_dark else "#1A1A1A")
    text = colors.get("text", "#A0A0A0" if is_dark else "#6B6B6B")
    text_light = colors.get("textLight", "#707070" if is_dark else "#B0B0B0")

    # Extended colors
    border_alpha = "0.12" if is_dark else "0.14"
    border_color = ink
    card_bg_alpha = "0.04" if is_dark else "0.04"

    # Derive additional colors
    def hex_to_rgb(h):
        h = h.lstrip("#")
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(r, g, b):
        return f"#{r:02x}{g:02x}{b:02x}"

    pr, pg, pb = hex_to_rgb(primary)
    ir, ig, ib = hex_to_rgb(ink)
    accent_light = f"rgba({pr}, {pg}, {pb}, 0.08)"
    accent_medium = f"rgba({pr}, {pg}, {pb}, 0.15)"
    border_rgba = f"rgba({ir}, {ig}, {ib}, {border_alpha})"
    card_bg = f"rgba({pr}, {pg}, {pb}, {card_bg_alpha})"

    # Build typography from textStyles
    ts = text_styles
    display_fs = ts.get("heroTitle", {}).get("fontSize", "64")
    headline_fs = ts.get("sectionHeadline", {}).get("fontSize", "48")
    coltitle_fs = ts.get("columnTitle", {}).get("fontSize", "28")
    cardtitle_fs = ts.get("cardTitle", {}).get("fontSize", "24")
    stat_fs = ts.get("statNumeral", {}).get("fontSize", "56")
    body_fs = ts.get("body", {}).get("fontSize", "18")
    bodysm_fs = ts.get("bodySm", {}).get("fontSize", "15")
    label_fs = ts.get("sectionLabel", {}).get("fontSize", "12")

    disp_ff = cfg["display_font"]
    body_ff = cfg["body_font"]
    disp_name = disp_ff.split(",")[0].strip("'\"")
    body_name = body_ff.split(",")[0].strip("'\"")

    lines = []
    lines.append("---")
    lines.append(f'version: alpha')
    lines.append(f'name: {cfg["name"]}')
    lines.append(f'description: >-')
    lines.append(f'  {cfg["description"]}')
    lines.append("")
    lines.append("colors:")
    lines.append(f'  bg: "{bg}"')
    lines.append(f'  primary: "{primary}"')
    lines.append(f'  text: "{ink}"')
    lines.append(f'  text-muted: "{text}"')
    lines.append(f'  text-light: "{text_light}"')
    lines.append(f'  accent-light: "{accent_light}"')
    lines.append(f'  accent-medium: "{accent_medium}"')
    lines.append(f'  border: "{border_rgba}"')
    lines.append(f'  card-bg: "{card_bg}"')
    if not is_dark:
        lines.append(f'  positive: "#059669"')
        lines.append(f'  negative: "#dc2626"')
    lines.append("")
    lines.append("typography:")
    lines.append(f"  h1:")
    lines.append(f'    fontFamily: "{disp_ff}"')
    lines.append(f'    fontWeight: 700')
    lines.append(f'    fontSize: "clamp(36px, 4.5vw, 56px)"')
    lines.append(f'    lineHeight: 1.1')
    lines.append(f'    letterSpacing: -0.02em')
    lines.append(f"  h2:")
    lines.append(f'    fontFamily: "{disp_ff}"')
    lines.append(f'    fontWeight: 600')
    lines.append(f'    fontSize: "clamp(24px, 3vw, 40px)"')
    lines.append(f'    lineHeight: 1.15')
    lines.append(f'    letterSpacing: -0.01em')
    lines.append(f"  h3:")
    lines.append(f'    fontFamily: "{disp_ff}"')
    lines.append(f'    fontWeight: 500')
    lines.append(f'    fontSize: "clamp(18px, 2vw, 28px)"')
    lines.append(f'    lineHeight: 1.2')
    lines.append(f"  h4-eyebrow:")
    lines.append(f'    fontFamily: "{body_ff}"')
    lines.append(f'    fontWeight: 600')
    lines.append(f'    fontSize: "clamp(11px, 1vw, 14px)"')
    lines.append(f'    lineHeight: 1.1')
    lines.append(f'    letterSpacing: 0.08em')
    lines.append(f'    textTransform: uppercase')
    lines.append(f'    color: "{{colors.primary}}"')
    lines.append(f"  body:")
    lines.append(f'    fontFamily: "{body_ff}"')
    lines.append(f'    fontWeight: 400')
    lines.append(f'    fontSize: "clamp(14px, 1.2vw, 18px)"')
    lines.append(f'    lineHeight: 1.6')
    lines.append(f'    color: "{{colors.text-muted}}"')
    lines.append(f"  body-sm:")
    lines.append(f'    fontFamily: "{body_ff}"')
    lines.append(f'    fontWeight: 400')
    lines.append(f'    fontSize: "clamp(12px, 1vw, 15px)"')
    lines.append(f'    lineHeight: 1.5')
    lines.append(f'    color: "{{colors.text-muted}}"')
    lines.append(f"  stat-value:")
    lines.append(f'    fontFamily: "{disp_ff}"')
    lines.append(f'    fontWeight: 700')
    lines.append(f'    fontSize: "clamp(36px, 3.5vw, 56px)"')
    lines.append(f'    lineHeight: 1.0')
    lines.append(f'    color: "{{colors.primary}}"')
    lines.append(f"  stat-label:")
    lines.append(f'    fontFamily: "{body_ff}"')
    lines.append(f'    fontWeight: 600')
    lines.append(f'    fontSize: "clamp(13px, 1.1vw, 16px)"')
    lines.append(f'    lineHeight: 1.3')
    lines.append(f'    color: "{{colors.text}}"')
    lines.append(f"  label:")
    lines.append(f'    fontFamily: "{body_ff}"')
    lines.append(f'    fontWeight: 600')
    lines.append(f'    fontSize: "clamp(10px, 0.85vw, 12px)"')
    lines.append(f'    lineHeight: 1.0')
    lines.append(f'    letterSpacing: 0.08em')
    lines.append(f'    textTransform: uppercase')
    lines.append(f'    color: "{{colors.primary}}"')
    lines.append(f"  caption:")
    lines.append(f'    fontFamily: "{body_ff}"')
    lines.append(f'    fontWeight: 400')
    lines.append(f'    fontSize: "clamp(10px, 0.9vw, 13px)"')
    lines.append(f'    lineHeight: 1.4')
    lines.append(f'    color: "{{colors.text-light}}"')
    lines.append(f"  quote:")
    lines.append(f'    fontFamily: "{disp_ff}"')
    lines.append(f'    fontWeight: 500')
    lines.append(f'    fontSize: "clamp(20px, 2.2vw, 32px)"')
    lines.append(f'    lineHeight: 1.35')
    lines.append(f'    color: "{{colors.text}}"')
    lines.append(f"  quote-mark:")
    lines.append(f'    fontFamily: "{disp_ff}"')
    lines.append(f'    fontWeight: 700')
    lines.append(f'    fontSize: "96px"')
    lines.append(f'    lineHeight: 0.5')
    lines.append(f'    color: "{{colors.primary}}"')
    lines.append(f'    opacity: 0.15')
    lines.append("")
    lines.append("spacing:")
    lines.append('  pad-slide-x: "48px"')
    lines.append('  pad-slide-y-top: "40px"')
    lines.append('  pad-slide-y-bottom: "48px"')
    lines.append('  pad-card: "24px 28px"')
    lines.append('  pad-card-sm: "16px 20px"')
    lines.append('  gap-lg: "32px"')
    lines.append('  gap-md: "20px"')
    lines.append('  gap-sm: "12px"')
    lines.append('  header-margin: "24px"')
    lines.append('  accent-line-width: "48px"')
    lines.append('  accent-line-height: "3px"')
    lines.append("")
    lines.append("canvas:")
    lines.append('  width: 1280')
    lines.append('  height: 720')
    lines.append('  background: "{colors.bg}"')
    lines.append("")
    lines.append("components:")
    lines.append("  card:")
    if is_dark:
        lines.append(f'    background: "{surface}"')
        lines.append(f'    border: "1px solid {{colors.border}}"')
        lines.append('    borderRadius: "4px"')
    else:
        lines.append('    background: "#FFFFFF"')
        lines.append(f'    border: "1px solid {{colors.border}}"')
        lines.append('    borderRadius: "8px"')
    lines.append('    padding: "24px 28px"')
    lines.append(f'    description: "Primary content card with subtle surface elevation."')
    lines.append("  accent-line:")
    lines.append('    width: "48px"')
    lines.append('    height: "3px"')
    lines.append('    background: "{colors.primary}"')
    lines.append('    borderRadius: "2px"')
    lines.append('    description: "Short accent rule under headlines."')
    lines.append("  tag-pill:")
    lines.append('    background: "{colors.accent-light}"')
    lines.append('    color: "{colors.primary}"')
    lines.append('    padding: "4px 12px"')
    lines.append('    borderRadius: "100px"')
    lines.append(f'    fontFamily: "{body_ff}"')
    lines.append('    fontWeight: 600')
    lines.append('    fontSize: "11px"')
    lines.append('    description: "Pill-shaped tag for categorization labels."')
    lines.append("  stat-card:")
    lines.append('    background: "transparent"')
    lines.append('    borderBottom: "1px solid {colors.border}"')
    lines.append('    padding: "16px 0"')
    lines.append('    description: "Stat display with bottom hairline — no background fill."')
    lines.append("---")
    return "\n".join(lines)


def build_decorations(colors: dict, cfg: dict) -> str:
    """Build the decorations block."""
    primary = colors.get("primary", "#1E88E5")
    bg = colors.get("background", "#121212")
    is_dark = cfg["dark"]
    bucket = cfg["bucket"]

    if bucket == "retro":
        return f"""decorations:
  cover-bg:
    draw: "Compose from dark canvas + CRT scanline overlay + pixel-grid pattern. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "L-shaped pixel corner brackets (4px stroke, {primary}) framing the title area."
    type: "accent"
    color: "{primary}"
  divider:
    draw: "Horizontal pixel-dash line made of small {primary} squares."
    type: "divider"
    color: "{primary}"
  scanlines:
    draw: "Horizontal line overlay at 4% opacity — CRT screen texture."
    type: "pattern"
    color: "#FFFFFF"
    opacity: 0.04
"""
    elif bucket == "playful":
        return f"""decorations:
  cover-bg:
    draw: "Compose from light canvas + scattered organic blob shapes at low opacity + small decorative dots. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Organic blob frame in corner with 3px {primary} stroke + small rotated accent shapes."
    type: "accent"
    color: "{primary}"
  divider:
    draw: "Hand-drawn-style scribble line (2px stroke, {primary}) with small dot accents."
    type: "divider"
    color: "{primary}"
  blob-pattern:
    draw: "Scattered organic blob shapes at 8% opacity across unused regions."
    type: "pattern"
    color: "{primary}"
    opacity: 0.08
"""
    else:
        # professional / tech-minimal
        return f"""decorations:
  cover-bg:
    draw: "Compose from solid background + subtle geometric line pattern + {primary} accent marks. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Thin {primary} corner brackets + center vertical accent bar."
    type: "accent"
    color: "{primary}"
  divider:
    draw: "Horizontal {primary} line with small center geometric mark."
    type: "divider"
    color: "{primary}"
  watermark:
    draw: "Oversized decorative numeral or glyph at 6% opacity in corner."
    type: "pattern"
    color: "{primary if is_dark else '#000000'}"
    opacity: 0.06
"""


def build_markdown_sections(colors: dict, cfg: dict) -> str:
    """Build the Markdown body sections."""
    primary = colors.get("primary", "#1E88E5")
    bg = colors.get("background", "#121212")
    ink = colors.get("ink", "#FFFFFF")
    text = colors.get("text", "#A0A0A0")
    surface = colors.get("surfaceAlt", bg)
    disp_ff = cfg["display_font"]
    body_ff = cfg["body_font"]
    disp_name = disp_ff.split(",")[0].strip("'\"")
    body_name = body_ff.split(",")[0].strip("'\"")

    sig = "\n".join("- " + s for s in cfg["signature_treatments"])
    dos = "\n".join("- " + d for d in cfg["dos"])
    donts = "\n".join("- " + d for d in cfg["donts"])

    return f"""
## Overview

{cfg["description"]}

The typographic stack runs two faces in strict role separation:

- **{disp_name}** carries every headline, display moment, and stat figure. Its weight and presence define the system's visual authority.
- **{body_name}** handles every body paragraph, bullet list, label, and caption. Its clarity and neutrality let the display face lead.

{cfg.get("density", "Medium density. Content slides hold 4-6 elements with structured grid alignment.")}

**Key Characteristics:**
{sig}

## Colors

### Palette
- **BG** (`{{colors.bg}}` — {bg}): The default slide background.
- **Primary** (`{{colors.primary}}` — {primary}): The signature accent color — used for stat numerals, eyebrow labels, accent lines, and emphasis.
- **Text** (`{{colors.text}}` — {ink}): Primary text color on the default background.
- **Text Muted** (`{{colors.text-muted}}` — {text}): Secondary body text — lighter weight in the hierarchy.
- **Text Light** (`{{colors.text-light}}` — {colors.get("textLight", "#707070")}): Tertiary text for captions, metadata, and hints.
- **Accent Light** (`{{colors.accent-light}}`): Subtle tint of the primary at 8% opacity — used for tag pill backgrounds and soft highlights.
- **Accent Medium** (`{{colors.accent-medium}}`): Medium tint of the primary at 15% opacity — used for hover states and selected regions.
- **Border** (`{{colors.border}}`): Translucent hairline for dividers, card borders, and structural lines.
- **Card BG** (`{{colors.card-bg}}`): Very subtle primary tint at 4% opacity — used for card fills when a distinct surface is needed.

### Defaults
- Default slide background: `{{colors.bg}}`.
- Default primary text: `{{colors.text}}`.
- Default body text: `{{colors.text-muted}}`.
- Default accent: `{{colors.primary}}`.
- Default border: `{{colors.border}}` at 1px solid.

## Typography

### Font Family
- **{disp_name}** ({cfg["cjk_display"]} for CJK): Display and headlines. The system's visual authority.
- **{body_name}** ({cfg["cjk_body"]} for CJK): Body, labels, captions, and UI text. The neutral supporting voice.

The roles are non-overlapping: display face for every headline moment; body face for every paragraph and label.

### Typography Scale

| Token | Size | Family | Weight | Use |
|---|---|---|---|---|
| `{{typography.h1}}` | clamp(36px, 4.5vw, 56px) | {disp_name} | 700 | Primary slide headline |
| `{{typography.h2}}` | clamp(24px, 3vw, 40px) | {disp_name} | 600 | Section sub-headline |
| `{{typography.h3}}` | clamp(18px, 2vw, 28px) | {disp_name} | 500 | Card titles, small headers |
| `{{typography.h4-eyebrow}}` | clamp(11px, 1vw, 14px) | {body_name} | 600 | Section eyebrow label (uppercase, wide tracking) |
| `{{typography.body}}` | clamp(14px, 1.2vw, 18px) | {body_name} | 400 | Standard body paragraph |
| `{{typography.body-sm}}` | clamp(12px, 1vw, 15px) | {body_name} | 400 | Small body, captions |
| `{{typography.stat-value}}` | clamp(36px, 3.5vw, 56px) | {disp_name} | 700 | Large stat numerals |
| `{{typography.stat-label}}` | clamp(13px, 1.1vw, 16px) | {body_name} | 600 | Stat supporting label |
| `{{typography.label}}` | clamp(10px, 0.85vw, 12px) | {body_name} | 600 | Tags, badges, metadata (uppercase) |
| `{{typography.caption}}` | clamp(10px, 0.9vw, 13px) | {body_name} | 400 | Captions, footnotes |
| `{{typography.quote}}` | clamp(20px, 2.2vw, 32px) | {disp_name} | 500 | Pull quotes, testimonials |
| `{{typography.quote-mark}}` | 96px | {disp_name} | 700 | Oversized opening quotation mark |

### Signature Treatments
{sig}

## Layout

### Canvas System
The system targets a 1280×720px slide canvas (16:9). Default slide padding is 48px horizontal and 40px top / 48px bottom.

### Padding and Gap Scale

| Token | Value | Use |
|---|---|---|
| `{{spacing.pad-slide-x}}` | 48px | Horizontal page margin |
| `{{spacing.pad-slide-y-top}}` | 40px | Top page margin |
| `{{spacing.pad-slide-y-bottom}}` | 48px | Bottom page margin |
| `{{spacing.pad-card}}` | 24px 28px | Standard card internal padding |
| `{{spacing.pad-card-sm}}` | 16px 20px | Compact card padding |
| `{{spacing.gap-lg}}` | 32px | Large gap between major sections |
| `{{spacing.gap-md}}` | 20px | Medium gap between related elements |
| `{{spacing.gap-sm}}` | 12px | Small gap between tightly coupled elements |
| `{{spacing.header-margin}}` | 24px | Space between eyebrow and headline |
| `{{spacing.accent-line-width}}` | 48px | Short accent rule width |
| `{{spacing.accent-line-height}}` | 3px | Accent rule thickness |

### Layout Templates

#### full-statement
One dominant statement centered on the slide. Eyebrow label above, large display text in the center, small accent mark below.
- **Composition**: Eyebrow (top-center) → Headline (center, 60% width) → Accent line (below headline)
- **Use**: Key conclusions, manifesto moments, single-message slides

#### asymmetric-split
Left 35-40% colored panel with title, right 60-65% body content.
- **Composition**: Left panel (shape, layer -1) → Panel title → Right body text
- **Use**: Topic overviews, chapter introductions, topic + elaboration

#### three-card-grid
Three equal cards arranged horizontally with icon/number, title, and description.
- **Composition**: Title (top) → Card 1/2/3 (equal width, evenly spaced)
- **Use**: Feature lists, process steps, comparisons

#### data-dashboard
Left half chart/table, right half 2-3 stat callouts.
- **Composition**: Chart (left) → Stat 1/2/3 (right column)
- **Use**: Data-heavy pages, metrics, reports

#### timeline-vertical
Vertical timeline with alternating left/right nodes.
- **Composition**: Central line → Nodes → Alternating left/right cards
- **Use**: Sequences, roadmaps, step-by-step processes

#### standard-content
Title at top, body content below, optional sidebar.
- **Composition**: Eyebrow → Title → Accent line → Body → Optional sidebar card
- **Use**: Conceptual explanations, analysis, fallback layout

## Depth and Elevation

{cfg["depth"]}

## Shapes and Treatment

{cfg["shapes"]}

## Do's and Don'ts

### Do
{dos}

### Don't
{donts}

## CJK & International Content

| Latin Font | CJK Fallback | Role |
|---|---|---|
| {disp_name} | {cfg["cjk_display"]} | Display / Headlines |
| {body_name} | {cfg["cjk_body"]} | Body / UI |

When generating CJK content, preserve the typographic hierarchy: display face for headlines, body face for paragraphs. CJK characters naturally run wider — allow slightly more line-height (1.7-1.8) and generous character spacing for readability.

## Notes

- **Mood**: {cfg["mood"]}
- **Personality**: {cfg.get("personality", cfg["mood"])}
- **Aesthetic Bucket**: {cfg["bucket"]}
- **Upgraded by**: upgrade_minimal_designs.py
"""


def upgrade_style(style_name: str) -> bool:
    """Upgrade a single minimal design.md to full format."""
    design_path = STYLES_DIR / style_name / "design.md"
    if not design_path.exists():
        print(f"  SKIP (not found): {style_name}")
        return False

    original = design_path.read_text(encoding="utf-8")

    # Parse existing content
    colors_yaml = extract_yaml_block(original, "Color System")
    text_yaml = extract_yaml_block(original, "Typography")
    # table_yaml = extract_yaml_block(original, "Table Styles")

    colors = parse_colors(colors_yaml)
    text_styles = parse_text_styles(text_yaml)

    # Extract original tableStyles YAML block to preserve it
    table_match = re.search(r"```yaml\ntableStyles:.*?```", original, re.DOTALL)
    table_styles_yaml = table_match.group(0) if table_match else ""

    cfg = STYLE_CONFIG.get(style_name)
    if not cfg:
        print(f"  SKIP (no config): {style_name}")
        return False

    # Build new content
    frontmatter = build_frontmatter(colors, text_styles, cfg)
    decorations = build_decorations(colors, cfg)
    markdown = build_markdown_sections(colors, cfg)

    # Build final content: frontmatter + decorations + preserved tableStyles + markdown
    parts = [frontmatter.rstrip(), decorations.rstrip()]
    if table_styles_yaml:
        parts.append(table_styles_yaml)
    parts.append(markdown.lstrip("\n"))
    new_content = "\n\n".join(parts)

    # Backup original
    backup_path = design_path.with_suffix(".md.bak")
    backup_path.write_text(original, encoding="utf-8")

    design_path.write_text(new_content, encoding="utf-8")

    old_lines = len(original.splitlines())
    new_lines = len(new_content.splitlines())
    print(f"  UPGRADED: {style_name} ({old_lines} → {new_lines} lines)")
    return True


def main():
    targets = [
        "apple-demo",
        "corporate-blue",
        "playful-pink",
        "retro-pixel",
        "tech-neon",
        "tech-neon-v2",
    ]
    upgraded = 0
    for name in targets:
        if upgrade_style(name):
            upgraded += 1
    print(f"\nDone: {upgraded}/{len(targets)} styles upgraded")


if __name__ == "__main__":
    main()
