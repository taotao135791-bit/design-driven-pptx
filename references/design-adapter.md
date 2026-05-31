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
- "45° diagonal hatch pattern" → Use decorations/pattern-hatch.svg via `elementType: image` with opacity, or shape with gradient fill
- "Accent line (80×4 rectangle)" → Shape rect at specified size with solid fill

### SVG Decorations

If the design.md defines a `decorations:` section, map each decoration to PPTD elements:

| Decoration Type | PPTD Implementation |
|-----------------|---------------------|
| pattern (e.g., hatch) | `elementType: image`, `src: "styles/<name>/decorations/pattern-hatch.svg"`, set `opacity` for subtlety |
| background (e.g., cover-bg) | `elementType: image`, `src: "styles/<name>/decorations/cover-bg.svg"`, full-slide bounds |
| accent (e.g., chapter frame) | `elementType: image`, `src: "styles/<name>/decorations/chapter-accent.svg"`, placed with opacity |
| divider | `elementType: image`, `src: "styles/<name>/decorations/divider.svg"`, placed between content sections |

Rules:
- SVG paths in `src` are relative to the design.md file location
- Use `opacity` to control subtlety (0.06–0.15 for textures, 0.3–0.5 for accents)
- For repeating patterns (hatch), use `fit: {mode: fill}` on the image element
- SVG decorations inherit the design system's color through the SVG file itself

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
