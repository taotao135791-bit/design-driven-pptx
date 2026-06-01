---
version: alpha
name: Playful Pink
description: >-
  A vibrant, energetic presentation system on a light gray canvas (#F5F5F5) with hot pink (#EC407A) as the single accent. Poppins carries headlines with rounded geometric warmth; Nunito handles body copy with friendly openness. The aesthetic is youthful, creative, and unapologetically bold — rounded cards, rotated elements, organic blob shapes, and a pink accent that delivers joy and confidence. Built for creative pitches, startup decks, educational content, and any presentation that needs personality and energy.

colors:
  bg: "#F5F5F5"
  primary: "#1E88E5"
  text: "#1A1A1A"
  text-muted: "#6B6B6B"
  text-light: "#B0B0B0"
  accent-light: "rgba(30, 136, 229, 0.08)"
  accent-medium: "rgba(30, 136, 229, 0.15)"
  border: "rgba(26, 26, 26, 0.14)"
  card-bg: "rgba(30, 136, 229, 0.04)"
  positive: "#059669"
  negative: "#dc2626"

typography:
  h1:
    fontFamily: "'Poppins', 'ZCOOL KuaiLe', sans-serif"
    fontWeight: 700
    fontSize: "clamp(36px, 4.5vw, 56px)"
    lineHeight: 1.1
    letterSpacing: -0.02em
  h2:
    fontFamily: "'Poppins', 'ZCOOL KuaiLe', sans-serif"
    fontWeight: 600
    fontSize: "clamp(24px, 3vw, 40px)"
    lineHeight: 1.15
    letterSpacing: -0.01em
  h3:
    fontFamily: "'Poppins', 'ZCOOL KuaiLe', sans-serif"
    fontWeight: 500
    fontSize: "clamp(18px, 2vw, 28px)"
    lineHeight: 1.2
  h4-eyebrow:
    fontFamily: "'Nunito', 'Yozai', sans-serif"
    fontWeight: 600
    fontSize: "clamp(11px, 1vw, 14px)"
    lineHeight: 1.1
    letterSpacing: 0.08em
    textTransform: uppercase
    color: "{colors.primary}"
  body:
    fontFamily: "'Nunito', 'Yozai', sans-serif"
    fontWeight: 400
    fontSize: "clamp(14px, 1.2vw, 18px)"
    lineHeight: 1.6
    color: "{colors.text-muted}"
  body-sm:
    fontFamily: "'Nunito', 'Yozai', sans-serif"
    fontWeight: 400
    fontSize: "clamp(12px, 1vw, 15px)"
    lineHeight: 1.5
    color: "{colors.text-muted}"
  stat-value:
    fontFamily: "'Poppins', 'ZCOOL KuaiLe', sans-serif"
    fontWeight: 700
    fontSize: "clamp(36px, 3.5vw, 56px)"
    lineHeight: 1.0
    color: "{colors.primary}"
  stat-label:
    fontFamily: "'Nunito', 'Yozai', sans-serif"
    fontWeight: 600
    fontSize: "clamp(13px, 1.1vw, 16px)"
    lineHeight: 1.3
    color: "{colors.text}"
  label:
    fontFamily: "'Nunito', 'Yozai', sans-serif"
    fontWeight: 600
    fontSize: "clamp(10px, 0.85vw, 12px)"
    lineHeight: 1.0
    letterSpacing: 0.08em
    textTransform: uppercase
    color: "{colors.primary}"
  caption:
    fontFamily: "'Nunito', 'Yozai', sans-serif"
    fontWeight: 400
    fontSize: "clamp(10px, 0.9vw, 13px)"
    lineHeight: 1.4
    color: "{colors.text-light}"
  quote:
    fontFamily: "'Poppins', 'ZCOOL KuaiLe', sans-serif"
    fontWeight: 500
    fontSize: "clamp(20px, 2.2vw, 32px)"
    lineHeight: 1.35
    color: "{colors.text}"
  quote-mark:
    fontFamily: "'Poppins', 'ZCOOL KuaiLe', sans-serif"
    fontWeight: 700
    fontSize: "96px"
    lineHeight: 0.5
    color: "{colors.primary}"
    opacity: 0.15

spacing:
  pad-slide-x: "48px"
  pad-slide-y-top: "40px"
  pad-slide-y-bottom: "48px"
  pad-card: "24px 28px"
  pad-card-sm: "16px 20px"
  gap-lg: "32px"
  gap-md: "20px"
  gap-sm: "12px"
  header-margin: "24px"
  accent-line-width: "48px"
  accent-line-height: "3px"

canvas:
  width: 1280
  height: 720
  background: "{colors.bg}"

components:
  card:
    background: "#FFFFFF"
    border: "1px solid {colors.border}"
    borderRadius: "8px"
    padding: "24px 28px"
    description: "Primary content card with subtle surface elevation."
  accent-line:
    width: "48px"
    height: "3px"
    background: "{colors.primary}"
    borderRadius: "2px"
    description: "Short accent rule under headlines."
  tag-pill:
    background: "{colors.accent-light}"
    color: "{colors.primary}"
    padding: "4px 12px"
    borderRadius: "100px"
    fontFamily: "'Nunito', 'Yozai', sans-serif"
    fontWeight: 600
    fontSize: "11px"
    description: "Pill-shaped tag for categorization labels."
  stat-card:
    background: "transparent"
    borderBottom: "1px solid {colors.border}"
    padding: "16px 0"
    description: "Stat display with bottom hairline — no background fill."
---

decorations:
  cover-bg:
    draw: "Compose from light canvas + scattered organic blob shapes at low opacity + small decorative dots. No pre-rendered background image."
    type: "background"
  chapter-accent:
    draw: "Organic blob frame in corner with 3px #1E88E5 stroke + small rotated accent shapes."
    type: "accent"
    color: "#1E88E5"
  divider:
    draw: "Hand-drawn-style scribble line (2px stroke, #1E88E5) with small dot accents."
    type: "divider"
    color: "#1E88E5"
  blob-pattern:
    draw: "Scattered organic blob shapes at 8% opacity across unused regions."
    type: "pattern"
    color: "#1E88E5"
    opacity: 0.08

## Table Styles

```yaml
tableStyles:
  default:
    fontSize: 15
    fontFamily: "Nunito, Yozai"
    headerFill: "{colors.primary}"
    headerColor: "{colors.text}"
    headerBold: true
    bodyFill: ["{colors.bg}", "{colors.card-bg}"]
    bodyColor: "{colors.text}"
    border:
      style: solid
      width: 1
      color: "{colors.border}"
```

## Overview

A vibrant, energetic presentation system on a light gray canvas (#F5F5F5) with hot pink (#EC407A) as the single accent. Poppins carries headlines with rounded geometric warmth; Nunito handles body copy with friendly openness. The aesthetic is youthful, creative, and unapologetically bold — rounded cards, rotated elements, organic blob shapes, and a pink accent that delivers joy and confidence. Built for creative pitches, startup decks, educational content, and any presentation that needs personality and energy.

The typographic stack runs two faces in strict role separation:

- **Poppins** carries every headline, display moment, and stat figure. Its weight and presence define the system's visual authority.
- **Nunito** handles every body paragraph, bullet list, label, and caption. Its clarity and neutrality let the display face lead.

Medium to dense. Playful slides can hold more elements than minimal systems — 5-7 elements per slide with overlapping and staggered positioning. The energy comes from density and variety, not sparsity.

**Key Characteristics:**
- Headlines use Poppins with positive letter-spacing (2-4px) — the rounded warmth is the system's voice
- Cards carry slight rotations (±2-3°) and organic asymmetric border-radii — never perfectly rectangular
- Every stat numeral is Poppins in {colors.primary} pink at 56px or larger
- Organic blob frames in corners with 3px {colors.primary} stroke — the doodle element is signature
- Accent elements include scribble lines, small rotated shapes, and scattered decorative dots

## Colors

### Palette
- **BG** (`{colors.bg}` — #121212): The default slide background.
- **Primary** (`{colors.primary}` — #1E88E5): The signature accent color — used for stat numerals, eyebrow labels, accent lines, and emphasis.
- **Text** (`{colors.text}` — #FFFFFF): Primary text color on the default background.
- **Text Muted** (`{colors.text-muted}` — #A0A0A0): Secondary body text — lighter weight in the hierarchy.
- **Text Light** (`{colors.text-light}` — #707070): Tertiary text for captions, metadata, and hints.
- **Accent Light** (`{colors.accent-light}`): Subtle tint of the primary at 8% opacity — used for tag pill backgrounds and soft highlights.
- **Accent Medium** (`{colors.accent-medium}`): Medium tint of the primary at 15% opacity — used for hover states and selected regions.
- **Border** (`{colors.border}`): Translucent hairline for dividers, card borders, and structural lines.
- **Card BG** (`{colors.card-bg}`): Very subtle primary tint at 4% opacity — used for card fills when a distinct surface is needed.

### Defaults
- Default slide background: `{colors.bg}`.
- Default primary text: `{colors.text}`.
- Default body text: `{colors.text-muted}`.
- Default accent: `{colors.primary}`.
- Default border: `{colors.border}` at 1px solid.

## Typography

### Font Family
- **Poppins** (ZCOOL KuaiLe for CJK): Display and headlines. The system's visual authority.
- **Nunito** (Yozai for CJK): Body, labels, captions, and UI text. The neutral supporting voice.

The roles are non-overlapping: display face for every headline moment; body face for every paragraph and label.

### Typography Scale

| Token | Size | Family | Weight | Use |
|---|---|---|---|---|
| `{typography.h1}` | clamp(36px, 4.5vw, 56px) | Poppins | 700 | Primary slide headline |
| `{typography.h2}` | clamp(24px, 3vw, 40px) | Poppins | 600 | Section sub-headline |
| `{typography.h3}` | clamp(18px, 2vw, 28px) | Poppins | 500 | Card titles, small headers |
| `{typography.h4-eyebrow}` | clamp(11px, 1vw, 14px) | Nunito | 600 | Section eyebrow label (uppercase, wide tracking) |
| `{typography.body}` | clamp(14px, 1.2vw, 18px) | Nunito | 400 | Standard body paragraph |
| `{typography.body-sm}` | clamp(12px, 1vw, 15px) | Nunito | 400 | Small body, captions |
| `{typography.stat-value}` | clamp(36px, 3.5vw, 56px) | Poppins | 700 | Large stat numerals |
| `{typography.stat-label}` | clamp(13px, 1.1vw, 16px) | Nunito | 600 | Stat supporting label |
| `{typography.label}` | clamp(10px, 0.85vw, 12px) | Nunito | 600 | Tags, badges, metadata (uppercase) |
| `{typography.caption}` | clamp(10px, 0.9vw, 13px) | Nunito | 400 | Captions, footnotes |
| `{typography.quote}` | clamp(20px, 2.2vw, 32px) | Poppins | 500 | Pull quotes, testimonials |
| `{typography.quote-mark}` | 96px | Poppins | 700 | Oversized opening quotation mark |

### Signature Treatments
- Headlines use Poppins with positive letter-spacing (2-4px) — the rounded warmth is the system's voice
- Cards carry slight rotations (±2-3°) and organic asymmetric border-radii — never perfectly rectangular
- Every stat numeral is Poppins in {colors.primary} pink at 56px or larger
- Organic blob frames in corners with 3px {colors.primary} stroke — the doodle element is signature
- Accent elements include scribble lines, small rotated shapes, and scattered decorative dots

## Layout

### Canvas System
The system targets a 1280×720px slide canvas (16:9). Default slide padding is 48px horizontal and 40px top / 48px bottom.

### Padding and Gap Scale

| Token | Value | Use |
|---|---|---|
| `{spacing.pad-slide-x}` | 48px | Horizontal page margin |
| `{spacing.pad-slide-y-top}` | 40px | Top page margin |
| `{spacing.pad-slide-y-bottom}` | 48px | Bottom page margin |
| `{spacing.pad-card}` | 24px 28px | Standard card internal padding |
| `{spacing.pad-card-sm}` | 16px 20px | Compact card padding |
| `{spacing.gap-lg}` | 32px | Large gap between major sections |
| `{spacing.gap-md}` | 20px | Medium gap between related elements |
| `{spacing.gap-sm}` | 12px | Small gap between tightly coupled elements |
| `{spacing.header-margin}` | 24px | Space between eyebrow and headline |
| `{spacing.accent-line-width}` | 48px | Short accent rule width |
| `{spacing.accent-line-height}` | 3px | Accent rule thickness |

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

Flat and color-based. No shadows, no gradients. Depth comes from: (1) rotation — tilted cards create perceived dimensionality; (2) color contrast — pink on light gray is inherently punchy; (3) organic shapes — blobs and scribbles create visual layers without lifting elements off the surface.

## Shapes and Treatment

All shapes are organic and rounded. Cards use asymmetric border-radius (e.g., 24px 8px 24px 8px). Blob frames use irregular curves. Even accent lines have hand-drawn irregularity. Sharp corners and perfect rectangles immediately collapse the playful register.

## Do's and Don'ts

### Do
- Rotate cards slightly (±2-3°) for a playful, sticker-sheet feel
- Use organic blob shapes with asymmetric border-radius as corner decorations
- Set stat numerals in bold {colors.primary} pink — they should feel celebratory
- Use hand-drawn-style scribble lines (2px stroke) as dividers and accents
- Apply generous internal padding (28-36px) inside cards — breathing room amplifies the playful energy
- Use uppercase labels with wide tracking in {colors.primary} for section navigation

### Don't
- Don't use sharp 0px corners — rounded, organic shapes are the system's DNA
- Don't use more than one accent color — hot pink is the solo chromatic voice
- Don't make layouts perfectly symmetrical — intentional asymmetry creates playful rhythm
- Don't use heavy shadows or gradients — depth comes from color contrast and rotation, not elevation
- Don't use formal serif fonts — Poppins and Nunito's rounded geometry is non-negotiable

## CJK & International Content

| Latin Font | CJK Fallback | Role |
|---|---|---|
| Poppins | ZCOOL KuaiLe | Display / Headlines |
| Nunito | Yozai | Body / UI |

When generating CJK content, preserve the typographic hierarchy: display face for headlines, body face for paragraphs. CJK characters naturally run wider — allow slightly more line-height (1.7-1.8) and generous character spacing for readability.

## Notes

- **Mood**: playful
- **Personality**: playful
- **Aesthetic Bucket**: playful
- **Upgraded by**: upgrade_minimal_designs.py

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

decoration-grammar:
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
    - "Thin accent line (1–2px) under titles or as a section divider in the primary accent color"
    - "Subtle gradient overlay (light-to-transparent) on cards or panels for gentle depth"
    - "Minimal geometric shape (circle, square, or line) in a corner at low opacity"
    - "Small icon or glyph mark near the eyebrow label as a navigational hint"
    - "Structured card grid with consistent spacing and alignment as the primary decorative rhythm
