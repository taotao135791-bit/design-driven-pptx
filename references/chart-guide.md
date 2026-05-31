# Chart Generation Guide

Guide for AI agents to automatically detect data points in content and generate appropriate charts.

## 1. Data Detection

When processing content for a `.page` file, scan for numeric data points:

### Signals That Indicate Chart-Worthy Data

| Signal | Example | Recommended Chart |
|--------|---------|-------------------|
| Time-series values | "Q1 revenue 120M, Q2 132M, Q3 101M" | line or bar |
| Comparative metrics | "Product A: 55%, Product B: 30%" | bar or pie |
| Growth/decline trends | "increased from 12% to 34% over 3 years" | line or area |
| Composition breakdown | "revenue split: product 55%, service 30%, licensing 15%" | pie or donut |
| Correlation pairs | "ad spend vs. conversion rate" | scatter |
| Ranked categories | "top 5 markets by size" | horizontal bar |

### Data Extraction Rules

1. **Preserve original numbers** — do not round or modify unless necessary for readability
2. **Extract labels** — category names, time periods, product names become `x` field
3. **Extract values** — numeric figures become `y` field(s)
4. **Handle missing data** — use `null` for gaps in time-series

## 2. Chart Type Selection

Choose chart type based on data semantics:

```
Data Type → Chart Type
─────────────────────────────
Trend over time        → line (smooth=true for gradual trends)
Comparison across cats → bar (vertical for few, horizontal for many)
Part-of-whole          → pie or donut (innerRadius: 0.4-0.6)
Correlation / XY       → scatter
Distribution           → bar (histogram style) or area
Mixed metrics          → combo (bar + line with secondary axis)
```

### Decision Flow

```
Does data have time dimension?
  ├─ Yes → Is the focus on rate of change?
  │         ├─ Yes → line (smooth if gradual)
  │         └─ No  → bar
  └─ No  → Are parts summing to a whole?
            ├─ Yes → pie / donut
            └─ No  → Are there 2 value dimensions?
                      ├─ Yes → scatter or bubble
                      └─ No  → bar (horizontal if labels are long)
```

## 3. Chart Configuration

### Color Inheritance

Charts **must** inherit colors from the design system theme:

```yaml
colors:
  - "$primary"        # Primary series
  - "$primaryDark"    # Secondary/comparison series
  - "$surfaceAlt"     # Tertiary series
  - "$textLight"      # Quaternary series
```

If theme only defines `primary` and `secondary`:
```yaml
colors: ["$primary", "$secondary", "$textLight", "$surfaceAlt"]
```

### Axis Styling

Default to clean axis styling:
```yaml
xAxis:
  gridLine: false
  label:
    color: "$text"
    fontSize: 11
yAxis:
  gridLine:
    style: dash
    color: "#E5E5E5"
  label:
    color: "$text"
    fontSize: 11
```

### Data Labels

Only show data labels when:
- Pie/donut charts (show percentage)
- Bar charts with < 6 categories (show value)
- Key highlight values on line charts

```yaml
dataLabels:
  show: true
  content: percentage  # or 'value'
  fontSize: 12
```

## 4. PPTD Chart Examples

### Trend Line Chart

```yaml
- elementId: chart-revenue
  elementType: chart
  bounds: [80, 200, 600, 380]
  type: line
  data:
    - {month: "Jan", revenue: 120, target: 110}
    - {month: "Feb", revenue: 132, target: 120}
    - {month: "Mar", revenue: 101, target: 130}
    - {month: "Apr", revenue: 134, target: 140}
  x: month
  y: [revenue, target]
  names: ["Actual", "Target"]
  colors: ["$primary", "$textLight"]
  seriesStyle:
    revenue: {smooth: true, width: 3, marker: {shape: circle, size: 6}}
    target: {line: dash, width: 2, marker: false}
  xAxis:
    gridLine: false
  yAxis:
    gridLine: {style: dash, color: "#E5E5E5"}
  legend: {position: top}
```

### Comparison Bar Chart

```yaml
- elementId: chart-products
  elementType: chart
  bounds: [80, 200, 600, 380]
  type: bar
  data:
    - {product: "Product A", share: 55}
    - {product: "Product B", share: 30}
    - {product: "Product C", share: 15}
  x: product
  y: [share]
  colors: ["$primary"]
  options:
    direction: vertical
  xAxis:
    gridLine: false
  yAxis:
    gridLine: {style: dash, color: "#E5E5E5"}
  legend: false
```

### Donut Chart

```yaml
- elementId: chart-composition
  elementType: chart
  bounds: [80, 200, 400, 400]
  type: pie
  data:
    - {category: "Product", value: 55}
    - {category: "Service", value: 30}
    - {category: "Licensing", value: 15}
  x: category
  y: [value]
  colors: ["$primary", "$primaryDark", "$surfaceAlt"]
  options:
    innerRadius: 0.5
  dataLabels:
    show: true
    content: percentage
    numberFormat: "0%"
  legend: {position: right}
```

### Combo Chart

```yaml
- elementId: chart-combo
  elementType: chart
  bounds: [80, 200, 600, 380]
  type: combo
  data:
    - {month: "Jan", revenue: 120, growthRate: 0.15}
    - {month: "Feb", revenue: 150, growthRate: 0.25}
  x: month
  y: [revenue, growthRate]
  names: ["Revenue", "Growth Rate"]
  colors: ["$primary", "$textLight"]
  seriesStyle:
    revenue: {type: bar}
    growthRate: {type: line, axis: secondary, smooth: true, width: 2}
  yAxis: {title: "Amount (10K)", numberFormat: "#,##0"}
  secondaryAxis: {title: "Growth Rate", numberFormat: "0%", min: 0, max: 0.5}
```

## 5. Content-Agent Chart Detection Prompt

When building content pages, apply this logic:

```
1. Scan the content paragraph for:
   - Numbers with units (%, $, M, K, etc.)
   - Time references (Q1, 2023, Jan, Month 1)
   - Category labels followed by values
   - Comparative language ("vs", "compared to", "increase/decrease")

2. If 3+ related data points found:
   a. Extract them into structured {label: value} pairs
   b. Choose chart type using the decision flow above
   c. Generate a chart element in the .page file
   d. Place chart in the visual hierarchy (usually right half or lower section)

3. If only 1-2 data points:
   - Use stat-numeral text treatment instead of chart
   - Large number + label is more impactful than a minimal chart
```

## 6. Design System Integration

Charts must respect the design system's:
- **Primary color** for the first/main series
- **Typography** for axis labels (use body font, not display font)
- **Density** — data-dense decks use smaller charts with data labels; editorial decks use larger charts with minimal chrome
- **No 3D effects** — flat 2D charts only
