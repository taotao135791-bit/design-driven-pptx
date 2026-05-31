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

## 6. CJK Adaptation Rules

When content is Chinese or mixed CJK+Latin:

1. **Line-height**: Bump CJK body to 1.7-1.8 (Hanzi need more breathing)
2. **Letter-spacing**: Zero out on Hanzi runs; keep only on Latin spans
3. **text-transform**: Drop `uppercase` on CJK labels — Chinese has no case
4. **Punctuation**: Full-width `，。：；` for Chinese; half-width for Latin
5. **No period on headlines**: Strip `。` from display strings
6. **Pangu spacing**: Insert space between Hanzi and Latin/digit runs (`AI 产品`)
7. **One font per sentence**: Don't switch CJK families mid-sentence

## 7. Chart Integration

When content contains data points, refer to `references/chart-guide.md` for:
- Data detection rules
- Chart type selection flow
- Color inheritance from theme
- PPTD chart syntax examples
