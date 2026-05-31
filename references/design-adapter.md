# Design.md to PPTD Theme Adapter

Map an arbitrary `design.md` visual design system into a PPTD-compatible theme and layout vocabulary.

## 1. Color Mapping

### Extract Colors

Read the design.md `colors:` section (or inline hex values). Identify:

| Role | How to Identify |
|------|----------------|
| **primary** | The signature/accent color — most frequent, used for borders, icons, emphasis |
| **background** | Default page background — usually light (cream/white/off-white) |
| **text / ink** | Main text color on the default background — usually dark |
| **secondary** | Supporting neutral — gray, mid-tone, used for body text |
| **surface colors** | Other full-region colors (e.g. coral, ink/black, cream) used in hard-edge splits |

### Map to PPTD Theme Colors

```yaml
theme:
  colors:
    primary: "<signature color>"
    primaryDark: "<darker variant of primary>"
    background: "<default page bg>"
    surfaceAlt: "<alternative surface color>"
    ink: "<dark text / dark surface color>"
    text: "<main body text color>"
    textLight: "<lighter text / tertiary>"
    white: "#FFFFFF"
```

Rules:
- If the design has exactly 3 surface colors (like Coral's coral/cream/ink), map all three.
- If the design defines opacity variants (e.g. `rgba(0,0,0,0.12)`), also define them as hex8: `"#1A1A1A1E"`.
- Always define `white` — used for card fills against dark/colored backgrounds.

## 2. Typography Mapping

### Extract Type Scale

Read design.md `typography:` section. For each token, map:

| Design Token | PPTD textStyle | Font Size Rule |
|-------------|----------------|----------------|
| hero-title / display | `heroTitle` | 44-64px for 1280x720 canvas |
| section-headline / h1 | `sectionHeadline` | 36-48px |
| column-title / h2 | `columnTitle` | 28-36px |
| card-title / h3 | `cardTitle` | 22-28px |
| stat-numeral / big-number | `statNumeral` | 48-64px, use primary color |
| body / paragraph | `body` | 18-20px (never < 18) |
| body-sm / caption | `bodySm` | 16px |
| label / eyebrow / meta | `sectionLabel` | 11-12px, uppercase, letterSpacing 2-4px |

### Font Family Mapping

**Rule 1: If design.md already declares a dual-font format like `"Liter, MiSans"` — use it as-is.**

**Rule 2: If design.md only declares a Latin font (e.g. `"Bebas Neue"`) — append the matching CJK font from the table below.**

**Rule 3: If design.md declares no fonts — use `"Liter, MiSans"` as the default.**

For CJK content:

| Design Latin Font | CJK Pairing | PPTD fontFamily |
|-------------------|-------------|-----------------|
| Bebas Neue | ZCOOL XiaoWei | `"Bebas Neue, ZCOOL XiaoWei"` |
| Inter | Yozai | `"Inter, Yozai"` |
| Liter | MiSans | `"Liter, MiSans"` |
| Any display | alimamashuheiti | `"<Latin>, alimamashuheiti"` |

Always use `"Latin, CJK"` dual-font format.

## 3. Layout Pattern Translation

Translate design.md layout patterns into PPTD element compositions:

### Hard-Edge Region Splits

Design pattern → PPTD implementation:
- "grid-template-rows: 35% 65%" → Two Shape rectangles stacked, each with solid fill
- "grid-template-columns: 1fr 1fr" → Two Shape rectangles side by side
- "grid-template-columns: 40% 60%" → Two Shape rectangles at 40/60 split

Use `elementType: shape`, `shapeName: rect`, `fill: {type: solid, color: "$color"}`.

### Accent Borders

Design pattern → PPTD implementation:
- "5px coral top border on cards" → Shape rect with `border: {style: solid, width: 5, color: "$primary"}` + white fill
- "4px coral left border on sidebar" → Shape rect with left border only (use 4-value border array)

### Decorative Elements

Design pattern → PPTD implementation:
- "Oversized background numeral at 12% opacity" → Text element with opacity: 0.12, large fontSize
- "45° diagonal hatch pattern" → Multiple thin rotated `shapeName: rect` elements with `opacity`, or shape with gradient fill
- "Accent line (80×4 rectangle)" → Shape rect at specified size with solid fill

### Programmatic Decorations

Decorations are drawn natively using `elementType: shape` (and occasionally `text`). Do **not** reference external SVG/PNG files.

#### Common Decorative Patterns → PPTD Equivalent

| Decorative Pattern | PPTD Implementation |
|--------------------|---------------------|
| Corner brackets (L-shapes) | `shapeName: custom` with SVG-like `path` property |
| Accent lines | `shapeName: rect` with small height and solid fill |
| Hatch patterns | Multiple thin rotated `shapeName: rect` elements |
| Scanlines | Multiple horizontal thin `shapeName: rect` elements |
| Dot grids | Multiple small `shapeName: rect` or `ellipse` elements |
| Background numerals | `elementType: text` with large `fontSize` + low `opacity` |
| Dividers | `shapeName: rect` or combination of rect elements |

#### Shape Properties for Decorations

**`opacity`** (number, 0.0–1.0)
Controls the transparency of the shape. Use low values for subtle textures and overlays:
- 0.06–0.15 for background textures and patterns
- 0.3–0.5 for accent decorations
- 0.6–0.9 for prominent decorative elements

**`shadow`** (object)
Adds a shadow effect to the shape:
```yaml
shadow:
  color: "#000000"
  blur: 0          # Use 0 for hard shadows, >0 for soft shadows
  offset: [4, 4]   # Use offset array, not offsetX/offsetY
  opacity: 0.2
```

**`path`** (string, required for `shapeName: custom`)
Defines a custom shape using an SVG-like path string. Format:
```
"width,height;M... L... C... Z"
```
The first segment specifies the path's bounding-box dimensions. The remainder is standard SVG path syntax.

**Example — L-shaped corner bracket:**
```yaml
elementType: shape
shapeName: custom
path: "24,24;M0 0 L24 0 L24 4 L4 4 L4 24 L0 24 Z"
fill:
  type: solid
  color: "$primary"
```

#### Rules
- All decorative elements must be composed from native `shape` and `text` elements
- Use `opacity` for subtlety — never rely on pre-rendered transparent images
- For repeating patterns, create multiple shape instances or use a single custom path
- Decorative colors should reference theme variables (e.g., `$primary`, `$ink`)

## 3a. Dynamic Color Adaptation (Optional)

Before finalizing the theme, detect content tone and adapt colors:

1. **Detect tone** from content source keywords (read `references/dynamic-color-adaptation.md`):
   - serious → reduce saturation 30%
   - creative → increase saturation 20%, boost contrast 15%
   - data_intensive → slight desaturation, boost contrast 10%

2. **Apply adjustments** to `primary` and `primaryDark` colors only.

3. **Validate contrast** — ensure adapted colors maintain WCAG AA against background.

Use `scripts/color_utils.py` for standalone color operations, or apply manually in the theme YAML.

## 4. Component Mapping

| Design Component | PPTD Implementation |
|-----------------|---------------------|
| Card (white fill + top border) | Shape rect with white fill + top border |
| Sidebar item (white fill + left border) | Shape rect with white fill + left border |
| Icon square (colored rect + glyph) | Shape rect with colored fill + overlapping Text |
| Timeline line | Shape straightConnector1 with thick border |
| Timeline dot | Shape ellipse with colored fill + cream border |
| Info bar | Shape rect (cream bg) + Text elements inside |
| Accent line | Shape rect (small, colored fill) |

## 5. Theme YAML Template

```yaml
theme:
  colors:
    primary: "<hex>"
    primaryDark: "<hex>"
    background: "<hex>"
    surfaceAlt: "<hex>"
    ink: "<hex>"
    text: "<hex>"
    textLight: "<hex>"
    white: "#FFFFFF"
  textStyles:
    heroTitle:
      fontSize: <48-64>
      color: "$ink"
      fontFamily: "<display font>"
      lineHeight: 0.95
      letterSpacing: <2-4>
    sectionHeadline:
      fontSize: <36-48>
      color: "$ink"
      fontFamily: "<display font>"
      lineHeight: 1.0
      letterSpacing: <2>
    columnTitle:
      fontSize: <28-36>
      color: "$ink"
      fontFamily: "<display font>"
      lineHeight: 1.0
      letterSpacing: <1-2>
    cardTitle:
      fontSize: <22-28>
      color: "$ink"
      fontFamily: "<display font>"
      lineHeight: 1.1
      letterSpacing: <1>
    statNumeral:
      fontSize: <48-64>
      color: "$primary"
      fontFamily: "<display font>"
      lineHeight: 1.0
    body:
      fontSize: <18-20>
      color: "$text"
      fontFamily: "<body font>"
      lineHeight: 1.6-1.7
    bodySm:
      fontSize: 16
      color: "$text"
      fontFamily: "<body font>"
      lineHeight: 1.5-1.6
    sectionLabel:
      fontSize: 11-12
      color: "$primary"
      fontFamily: "<body font>"
      lineHeight: 1.0
      letterSpacing: <3-4>
  tableStyles:
    default:
      fontSize: 16
      fontFamily: "<body font>"
      headerFill: "$primary"
      headerColor: "$white"
      headerBold: true
      bodyFill: ["$white", "$background"]
      bodyColor: "$ink"
      border:
        style: solid
        width: 1
        color: "<border color>"
```

## 6. Layout Template System

Define 6 universal content-page layout templates that apply across all 34 styles. Each template provides a proven composition pattern with PPTD element specifications.

### 6.1 full-statement

**When to use:** Key conclusion, manifesto statement, or single core idea that deserves maximum emphasis.

**Content pattern:** 1 dominant statement + optional eyebrow label + optional supporting subtitle.

**PPTD composition:**
| Element | elementType | layer | Approximate bounds |
|---------|-------------|-------|--------------------|
| Background surface | shape (rect) | -1 | Full bleed or lower 60% |
| Decorative numeral (oversized, low opacity) | text | -1 | Behind statement, 12-15% opacity |
| Eyebrow label | text | 1 | Top-center or top-left, 11-12px uppercase |
| Main statement | text | 1 | Center or upper-center, 44-64px, max 3 lines |
| Accent line | shape (rect) | 2 | Under or beside statement, 80×4px |

**Style-specific adaptation:**
- `coral`, `bold-poster`: Hard-edge surface split (lower 60% colored, top 40% cream)
- `playful`: Rotated card behind statement at -3° angle
- `monochrome`, `vellum`: Ink-toned background numeral, no color panels
- `8-bit-orbit`: Neon-accent underline with scanline texture

### 6.2 asymmetric-split

**When to use:** Topic overview with 2-3 sub-sections, or when content naturally divides into topic + elaboration.

**Content pattern:** Title/heading + 2-3 body paragraphs or bullet groups.

**PPTD composition:**
| Element | elementType | layer | Approximate bounds |
|---------|-------------|-------|--------------------|
| Left colored panel | shape (rect) | -1 | [0, 0, 450-500, 720] |
| Left panel title | text | 1 | Inside left panel, centered or top-aligned |
| Left panel subtitle/label | text | 1 | Below title inside panel |
| Right body content | text | 1 | [520-560, 80, 680-720, 560] |
| Accent divider | shape (rect) | 2 | Between panels or top of right area |

**Style-specific adaptation:**
- `coral`, `broadside`: Hard-edge 40/60 split with coral left panel
- `cartesian`, `cobalt-grid`: Left panel uses grid-pattern fill or secondary surface
- `biennale-yellow`: Left panel in signature yellow, right on white
- `capsule`: Rounded-corner left panel (use `shapeName: rect` with border radius if supported, else rect)

### 6.3 three-card-grid

**When to use:** Feature list, process steps (3-5 items), comparisons, or any content with parallel items.

**Content pattern:** 3-5 equal items, each with icon/number + title + short description.

**PPTD composition:**
| Element | elementType | layer | Approximate bounds |
|---------|-------------|-------|--------------------|
| Page title | text | 1 | Top, full width |
| Card backgrounds (3) | shape (rect) | 0 | Equal thirds: [80, 220, 340, 400], [440, 220, 340, 400], [800, 220, 340, 400] |
| Card top borders (3) | shape (rect) | 2 | 4px height across top of each card |
| Icon/number per card | text or shape | 1 | Top of card, 48-64px numeral or 32px icon area |
| Card titles (3) | text | 1 | Below icon, 22-28px |
| Card descriptions (3) | text | 1 | Below title, 16-18px body |

**Style-specific adaptation:**
- `playful`: Cards rotated ±2°, overlapping slightly
- `coral`, `bold-poster`: Cards with 4-5px top border in primary color, white fill
- `8-bit-orbit`: Cards with pixel-corner decorations (small squares at corners)
- `monochrome`, `vellum`: No card borders — use subtle gray dividers or ink-toned cards

### 6.4 data-dashboard

**When to use:** Data-heavy pages with 3+ numeric metrics, charts, or tables.

**Content pattern:** 1 primary chart/table + 2-3 stat callouts, or multiple related data visualizations.

**PPTD composition:**
| Element | elementType | layer | Approximate bounds |
|---------|-------------|-------|--------------------|
| Page title | text | 1 | Top |
| Primary chart or table | chart or table | 1 | Left half: [80, 160, 560, 480] |
| Stat callout 1 | text | 1 | Right column, upper |
| Stat callout 2 | text | 1 | Right column, middle |
| Stat callout 3 | text | 1 | Right column, lower |
| Callout accent lines | shape (rect) | 2 | Under each stat number |

**Style-specific adaptation:**
- `creative-mode`: Chart uses full palette cycling; stat numbers in alternating colors
- `monochrome`, `vellum`: Chart in ink tones + single accent; stats in dark gray
- `8-bit-orbit`: Neon grid lines, dark background panel behind chart
- `coral`: White card behind chart with coral top border; stats on cream background

### 6.5 timeline-vertical

**When to use:** Sequences, roadmaps, ladders, or any 4+ ordered steps with progression.

**Content pattern:** 4-8 ordered steps, each with date/phase + title + description.

**PPTD composition:**
| Element | elementType | layer | Approximate bounds |
|---------|-------------|-------|--------------------|
| Central vertical line | shape (straightConnector1 or rect) | 0 | [630-650, 120, 4, 520] |
| Timeline nodes (4+) | shape (ellipse) | 1 | Centered on line, 16-24px diameter |
| Left-side step cards | shape (rect) + text | 0/1 | Alternating left: [120, Y, 460, 100] |
| Right-side step cards | shape (rect) + text | 0/1 | Alternating right: [700, Y, 460, 100] |
| Node connectors | shape (rect) | 0 | Horizontal lines from node to cards |

**Style-specific adaptation:**
- `coral`, `broadside`: Nodes in coral with cream borders; alternating cream/white cards
- `8-bit-orbit`: Glowing neon nodes; dark card panels
- `playful`: Nodes as rotated squares or stars
- `monochrome`, `vellum`: Nodes as ink circles; subtle gray card backgrounds

### 6.6 standard-content

**When to use:** Conceptual explanations, analysis, fallback when no other template matches.

**Content pattern:** Title + body paragraphs, possibly with 1 sidebar or callout box.

**PPTD composition:**
| Element | elementType | layer | Approximate bounds |
|---------|-------------|-------|--------------------|
| Page title | text | 1 | Top-left, 36-48px |
| Body content | text | 1 | Main area: [80, 160, 700, 480] |
| Optional sidebar card | shape (rect) | 0 | Right: [820, 160, 380, 480] |
| Sidebar title | text | 1 | Inside sidebar |
| Sidebar content | text | 1 | Inside sidebar |
| Accent line under title | shape (rect) | 2 | [80, 140, 120, 4] |

**Style-specific adaptation:**
- All styles: This is the safest fallback — follow the style's standard title/body spacing
- `coral`, `bold-poster`: Add coral accent line under title
- `capsule`: Rounded sidebar card with capsule-shaped pill label
- `cartesian`: Grid-aligned body columns

### Layout Template Extraction

When reading a source `design.md`, the main agent MUST:

1. Look for a `layouts:` or `layout-templates:` section in the source design document.
2. If present, extract all defined layouts (name, description, composition, bounds) and include them verbatim in the generated `design.md` under a `layouts:` catalog section.
3. If no layouts section exists in the source, apply the 6 universal templates defined above and include them as the default layout catalog in the generated `design.md`.
4. Map any style-specific layout variants (e.g., "coral uses 40/60 split", "playful uses rotated cards") into the `layouts:` section as `styleOverrides` or inline adaptation notes.
5. The layout catalog must be written in the generated `design.md` so that subagents can reference it during page construction.

## 5a. CSS Unit Conversion Guide

Design.md often uses CSS viewport-relative units. For PPTD (fixed 1280×720 canvas), convert as follows:

| CSS Expression | PPTD px Equivalent | Notes |
|---------------|-------------------|-------|
| `clamp(48px, 10vw, 128px)` | 128 | Use the max value for display text |
| `clamp(32px, 5vw, 64px)` | 64 | Use the max value for headlines |
| `clamp(24px, 3.5vw, 45px)` | 45 | Use the max value for subheads |
| `min(120px, 9vw, 13vh)` | 120 | Use the min value as the cap |
| `clamp(14.4px, 1.2vw, 18.4px)` | 18 | Use the max for body text |
| `1vw` | 12.8px | 1vw = 12.8px on 1280px canvas |
| `1vh` | 7.2px | 1vh = 7.2px on 720px canvas |

Rules:
1. For display/headline fonts: use the **upper bound** of clamp() (the designed maximum)
2. For body text: use the **upper bound** as well (PPT is viewed at full size)
3. For padding/margins with clamp(): use the **middle value** or calculate from vw/vh
4. Never use `vw/vh/em/rem` directly in PPTD — always convert to px

## 7. CJK Adaptation Rules

When content is Chinese or mixed CJK+Latin:

1. **Line-height**: Bump CJK body to 1.7-1.8 (Hanzi need more breathing)
2. **Letter-spacing**: Zero out on Hanzi runs; keep only on Latin spans
3. **text-transform**: Drop `uppercase` on CJK labels — Chinese has no case
4. **Punctuation**: Full-width `，。：；` for Chinese; half-width for Latin
5. **No period on headlines**: Strip `。` from display strings
6. **Pangu spacing**: Insert space between Hanzi and Latin/digit runs (`AI 产品`)
7. **One font per sentence**: Don't switch CJK families mid-sentence

## 8. Chart Integration

When content contains data points, refer to `references/chart-guide.md` for:
- Data detection rules
- Chart type selection flow
- Color inheritance from theme
- PPTD chart syntax examples
