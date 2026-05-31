# Design Rationale: full_test

**Generated**: 2026-05-31 21:02
**Total Pages**: 6
**Design System**: design.md

---

## Executive Summary

This presentation uses **4 distinct layout patterns** across 6 slides. 7 data visualizations are employed to transform raw numbers into actionable insights. The design follows a **modern** aesthetic with **#000000** as the primary accent against a **#F5F5F5** background.

### Layout Distribution

- **standard-content**: 3 slide(s)
- **cover-hero**: 1 slide(s)
- **multi-card-grid**: 1 slide(s)
- **data-table**: 1 slide(s)

---

## Per-Page Design Decisions

### Slide 1 — `pages/p1_cover.page`

**Layout**: cover-hero

> Large title with supporting metadata, establishes visual tone

**Composition**: 1×text | Density: airy (0.1)

**Typography Hierarchy**:

| Level | Size | Preview |
|-------|------|---------|
| display | 72px | COMPREHENSIVE TEST... |

**Color Strategy**:

- **ink** (`$ink`): Used in 1 element(s) — title(text:text)

**Whitespace**: generous whitespace creates breathing room and focuses attention (content covers 10% of slide)

---

### Slide 2 — `pages/p2_budget.page`

**Layout**: standard-content

> Default content layout with title and body

**Composition**: 2×chart, 1×text | Density: balanced (0.56)

**Typography Hierarchy**:

| Level | Size | Preview |
|-------|------|---------|
| display | 18px | • UAC $80K（60%） • Search $30K（... |

**Color Strategy**:

- **text** (`$text`): Used in 1 element(s) — text(text:text)

**Data Visualization**:

- `viz-text` (pie-chart): Pie chart for 4 data points. Pie charts effectively show part-to-whole relationships when categories are few (≤6)
- `viz-text` (pie-chart): Pie chart for 4 data points. Pie charts effectively show part-to-whole relationships when categories are few (≤6)

**Whitespace**: balanced content-to-whitespace ratio (content covers 56% of slide)

---

### Slide 3 — `pages/p3_trend.page`

**Layout**: standard-content

> Default content layout with title and body

**Composition**: 2×chart, 1×text | Density: dense (0.91)

**Typography Hierarchy**:

| Level | Size | Preview |
|-------|------|---------|
| display | 18px | Q1: 5000 Q2: 15000 Q3: 32000 Q... |

**Color Strategy**:

- **text** (`$text`): Used in 1 element(s) — text(text:text)

**Data Visualization**:

- `viz-text` (line-chart): Line chart for 4 data points. Line charts reveal trends and patterns over time or ordered categories
- `viz-text` (line-chart): Line chart for 4 data points. Line charts reveal trends and patterns over time or ordered categories

**Whitespace**: dense information layout maximizes content per slide (content covers 91% of slide)

---

### Slide 4 — `pages/p4_compare.page`

**Layout**: standard-content

> Default content layout with title and body

**Composition**: 2×chart, 1×text | Density: dense (0.74)

**Typography Hierarchy**:

| Level | Size | Preview |
|-------|------|---------|
| display | 18px | Competitor A: 45% Competitor B... |

**Color Strategy**:

- **text** (`$text`): Used in 1 element(s) — text(text:text)

**Data Visualization**:

- `viz-text` (bar-chart): Bar chart for 4 data points. Bar charts enable easy comparison across discrete categories
- `viz-text` (bar-chart): Bar chart for 4 data points. Bar charts enable easy comparison across discrete categories

**Whitespace**: dense information layout maximizes content per slide (content covers 74% of slide)

---

### Slide 5 — `pages/p5_timeline.page`

**Layout**: multi-card-grid

> 10 cards for dense information architecture

**Composition**: 17×text, 10×shape | Density: balanced (0.37)

**Typography Hierarchy**:

| Level | Size | Preview |
|-------|------|---------|
| display | 18px | Step 1: Launch MVP Step 2: See... |
| display | 18px | 1... |
| display | 18px | 2... |
| display | 18px | 3... |
| display | 18px | 4... |

**Color Strategy**:

- **text** (`$text`): Used in 9 element(s) — text(text:text), tl-desc-0(text:text)
- **primary** (`$primary`): Used in 18 element(s) — tl-line(shape:fill), tl-node-0(shape:fill)

**Whitespace**: balanced content-to-whitespace ratio (content covers 37% of slide)

---

### Slide 6 — `pages/p6_table.page`

**Layout**: data-table

> Structured tabular data for precise reference

**Composition**: 1×table | Density: balanced (0.48)

**Data Visualization**:

- `tbl` (table): Table with 3 rows × 3 columns for precise data reference. Compact table size maintains readability without overwhelming the slide

**Whitespace**: balanced content-to-whitespace ratio (content covers 48% of slide)

---


## Underlying Design Principles

The following principles guided the design decisions throughout this deck:

1. **Visual Hierarchy Through Scale**: Headlines are 3–4× larger than body text, creating immediate scanability. This follows the principle that users scan, not read.

2. **Color as Navigation**: The primary accent color (`primary`) is reserved for the most important information on each slide — typically data callouts or key takeaways. This trains the viewer's eye to find what matters first.

3. **Density Rhythm**: Cover and chapter pages are intentionally sparse (airy), while content pages carry more information (balanced to dense). This creates a breathing pattern that prevents visual fatigue.

4. **Data Before Decoration**: Every chart and table serves a communicative purpose. The choice of chart type (pie for parts, bar for comparison, line for trends) is determined by the data's story, not aesthetics alone.

5. **Consistency Through System**: All 19 slides share the same 8-color palette, 2-font system, and spacing grid. This consistency reduces cognitive load and builds brand recognition.
