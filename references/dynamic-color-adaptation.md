# Dynamic Color Adaptation

Adapt design system colors based on content emotional tone and information density.

## 1. Content Tone Detection

The main agent analyzes the content source to determine emotional tone:

| Tone Indicator | Keywords / Signals |
|----------------|-------------------|
| **Serious / Formal** | "report", "analysis", "audit", "compliance", "risk", "regulation", "financial", "legal" |
| **Creative / Playful** | "launch", "concept", "vision", "innovation", "campaign", "brand", "creative" |
| **Data-Intensive** | "metrics", "KPI", "dashboard", "statistics", "benchmark", "growth rate", "%", "$" |
| **Educational** | "tutorial", "guide", "course", "learning", "workshop", "training" |
| **Promotional** | "offer", "discount", "limited", "exclusive", "new arrival", "sale" |

## 2. Adaptation Rules

### Tone → Color Adjustment Mapping

```yaml
serious:
  saturation_factor: 0.7      # Reduce saturation by 30%
  lightness_factor: 1.0       # Keep lightness
  contrast_boost: 1.0         # No contrast change
  description: "Mute vibrant colors for professional gravitas"

creative:
  saturation_factor: 1.2      # Increase saturation by 20%
  lightness_factor: 1.0
  contrast_boost: 1.15        # Increase contrast by 15%
  description: "Amplify colors for energetic impact"

data_intensive:
  saturation_factor: 0.85     # Slightly reduce saturation
  lightness_factor: 1.05      # Slightly lighten
  contrast_boost: 1.1         # Increase contrast for readability
  description: "Optimize for data readability and hierarchy"

educational:
  saturation_factor: 0.9
  lightness_factor: 1.02
  contrast_boost: 1.05
  description: "Warm and approachable without losing clarity"

promotional:
  saturation_factor: 1.15
  lightness_factor: 1.0
  contrast_boost: 1.1
  description: "Vibrant and attention-grabbing"
```

### Which Colors to Adapt

Apply adjustments to:
- `primary` — main accent color
- `primaryDark` — darker variant
- `surfaceAlt` — alternative surface

**Do NOT adapt**:
- `background` / `white` — keep neutral
- `ink` / `text` — keep readable dark
- `textLight` — subtle change only if needed

### Adaptation Formula

For each adaptable color:
1. Convert hex → HSL
2. Apply: `s = clamp(s * saturation_factor, 0, 1)`
3. Apply: `l = clamp(l * lightness_factor, 0.05, 0.95)`
4. Apply contrast boost: push l away from 0.5
5. Convert HSL → hex

## 3. Implementation in Design Adapter

In `references/design-adapter.md` step 2 (Adapt Design → PPTD Theme), add:

```
### 2a. Detect Content Tone

Read the content source and classify tone into one of: serious, creative, data_intensive, educational, promotional.

Default: "serious" for business reports, "creative" for product launches.

### 2b. Apply Color Adjustments

Use the tone mapping above to adjust primary colors. Write the adjusted hex values into the theme.

Example:
- Original primary: #E85D5D (coral)
- Tone: serious (saturation_factor: 0.7)
- Adjusted primary: #C97A7A (muted coral)
```

## 4. Information Density Adjustment

Beyond tone, adjust based on information density:

| Density | Signal | Adjustment |
|---------|--------|------------|
| Low (≤10 pages) | Few slides, sparse content | Increase whitespace, use larger fonts, keep colors vibrant |
| Medium (11-20 pages) | Standard deck | Default design system values |
| High (21-35 pages) | Dense content, many data points | Reduce font sizes slightly, increase contrast, add more accent borders |
| Very High (>35 pages) | Dashboard/report style | Use cards with borders, maximize information hierarchy, consider muted palette |

## 5. Validation

After adaptation, verify:
- [ ] Background + text still has WCAG AA contrast (4.5:1)
- [ ] Primary color on background is distinguishable
- [ ] No color clashes between adapted primary and surfaceAlt
- [ ] Chart colors remain distinguishable after adaptation

## 6. Tool Reference

The converter (`scripts/pptd2pptx.py`) includes color utility functions:
- `adjust_saturation(hex, factor)`
- `adjust_lightness(hex, factor)`
- `adjust_contrast(hex, factor)`

Use `scripts/color_utils.py` for standalone color operations.
