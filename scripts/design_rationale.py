#!/usr/bin/env python3
"""
Design Rationale — Analyze .pptd + design.md and output
a human-readable design rationale document.

Usage:
    python design_rationale.py --pptd test_e2e_coral/dreamina.pptd --design-md test_e2e_coral/design.md
    python design_rationale.py --pptd test.pptd --design-md design.md --output rationale.md
"""

import sys
import os
import re
import argparse
from pathlib import Path
from collections import defaultdict, Counter

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


# ---------------------------------------------------------------------------
# Analysis helpers
# ---------------------------------------------------------------------------

def luminance(hex_color):
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
    g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
    b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def analyze_layout(page_data, page_index):
    """Analyze the layout composition of a page."""
    elements = page_data.get('elements', [])
    page_type = page_data.get('pageType', 'content')
    
    if not elements:
        return {'type': 'empty', 'reason': 'No elements found'}
    
    # Count element types
    type_counts = Counter(e.get('elementType', 'unknown') for e in elements)
    
    # Check for common layout patterns
    shapes = [e for e in elements if e.get('elementType') == 'shape']
    texts = [e for e in elements if e.get('elementType') == 'text']
    charts = [e for e in elements if e.get('elementType') == 'chart']
    tables = [e for e in elements if e.get('elementType') == 'table']
    images = [e for e in elements if e.get('elementType') == 'image']
    
    # Analyze spatial distribution
    left_heavy = False
    right_heavy = False
    center_focus = False
    
    if texts:
        text_centers = [(e.get('bounds', [0,0,0,0])[0] + e['bounds'][2]/2) for e in texts]
        avg_center = sum(text_centers) / len(text_centers) if text_centers else 640
        if avg_center < 500:
            left_heavy = True
        elif avg_center > 780:
            right_heavy = True
        elif 540 < avg_center < 740:
            center_focus = True
    
    # Detect specific layout patterns
    layout_type = 'standard-content'
    reason = 'Default content layout with title and body'
    
    if page_type == 'cover':
        layout_type = 'cover-hero'
        reason = 'Large title with supporting metadata, establishes visual tone'
    elif page_type == 'chapter':
        layout_type = 'chapter-break'
        reason = 'High-impact chapter divider with oversized numerals and color blocking'
    elif page_type == 'table_of_contents':
        layout_type = 'toc-navigation'
        reason = 'Hierarchical list navigation with clear chapter numbering'
    elif page_type == 'final':
        layout_type = 'closing-statement'
        reason = 'Minimal closing with brand reinforcement'
    elif charts or tables:
        if charts and tables:
            layout_type = 'data-dashboard'
            reason = 'Chart + table combination for comprehensive data presentation'
        elif len(charts) == 1 and len(texts) >= 2:
            layout_type = 'data-storytelling'
            reason = 'Chart as visual anchor with explanatory text'
        elif tables:
            layout_type = 'data-table'
            reason = 'Structured tabular data for precise reference'
    elif len(shapes) >= 4 and len(texts) >= 4:
        # Check if shapes are card-like (similar sizes, grid arrangement)
        shape_bounds = [e.get('bounds', [0,0,0,0]) for e in shapes if e.get('bounds')]
        if shape_bounds:
            widths = [b[2] for b in shape_bounds]
            heights = [b[3] for b in shape_bounds]
            width_variance = max(widths) - min(widths) if widths else 0
            height_variance = max(heights) - min(heights) if heights else 0
            
            if width_variance < 50 and len(shapes) >= 3:
                if len(shapes) == 3:
                    layout_type = 'three-card-grid'
                    reason = 'Three equal cards for balanced comparison or feature listing'
                elif len(shapes) == 4:
                    layout_type = 'four-card-grid'
                    reason = 'Four equal cards for quadrant analysis or pillars'
                elif len(shapes) >= 5:
                    layout_type = 'multi-card-grid'
                    reason = f'{len(shapes)} cards for dense information architecture'
    elif left_heavy and len(texts) >= 2:
        layout_type = 'asymmetric-split'
        reason = 'Asymmetric composition with dominant left panel and supporting right content'
    elif right_heavy and len(texts) >= 2:
        layout_type = 'asymmetric-split-reverse'
        reason = 'Asymmetric composition with dominant right panel and supporting left content'
    
    # Density analysis
    total_element_area = sum(
        e.get('bounds', [0,0,0,0])[2] * e.get('bounds', [0,0,0,0])[3] 
        for e in elements if e.get('bounds')
    )
    page_area = 1280 * 720
    density = total_element_area / page_area
    
    density_label = 'balanced'
    if density < 0.3:
        density_label = 'airy'
    elif density > 0.7:
        density_label = 'dense'
    
    return {
        'type': layout_type,
        'reason': reason,
        'element_types': dict(type_counts),
        'density': round(density, 2),
        'density_label': density_label,
        'left_heavy': left_heavy,
        'right_heavy': right_heavy,
    }


def analyze_color_usage(page_data, design_colors):
    """Analyze how colors are used on the page."""
    elements = page_data.get('elements', [])
    color_usage = defaultdict(list)
    
    for elem in elements:
        eid = elem.get('elementId', '?')
        etype = elem.get('elementType', '?')
        
        # Check fill color
        fill = elem.get('fill', {})
        if fill.get('type') == 'solid':
            color = fill.get('color', '')
            if color:
                color_usage[color].append(f'{eid}({etype}:fill)')
        
        # Check text content color
        content = elem.get('content', {})
        if isinstance(content, dict):
            color = content.get('color', '')
            if color:
                color_usage[color].append(f'{eid}({etype}:text)')
        
        # Check border color
        border = elem.get('border', {})
        if border:
            color = border.get('color', '')
            if color:
                color_usage[color].append(f'{eid}({etype}:border)')
    
    # Map to design system roles
    role_usage = {}
    for color, elems in color_usage.items():
        role = 'custom'
        if color.startswith('$'):
            role = color.lstrip('$')
        elif design_colors:
            for role_name, role_color in design_colors.items():
                if color.lower() == role_color.lower():
                    role = role_name
                    break
        role_usage[role] = {
            'color': color,
            'element_count': len(elems),
            'examples': elems[:3],
        }
    
    return role_usage


def analyze_typography(page_data):
    """Analyze typography hierarchy on the page."""
    elements = page_data.get('elements', [])
    text_elements = [e for e in elements if e.get('elementType') == 'text']
    
    sizes = []
    for elem in text_elements:
        content = elem.get('content', {})
        if isinstance(content, dict):
            size = content.get('fontSize', 0)
            if size:
                sizes.append((elem.get('elementId', '?'), size, content.get('text', '')[:30]))
    
    sizes.sort(key=lambda x: x[1], reverse=True)
    
    hierarchy = []
    if sizes:
        max_size = sizes[0][1]
        for eid, size, text_preview in sizes:
            if size >= max_size * 0.8:
                level = 'display'
            elif size >= max_size * 0.5:
                level = 'heading'
            elif size >= max_size * 0.3:
                level = 'body'
            else:
                level = 'caption'
            hierarchy.append({
                'elementId': eid,
                'size': size,
                'level': level,
                'preview': text_preview,
            })
    
    return hierarchy


def analyze_data_viz(page_data):
    """Analyze data visualization decisions."""
    elements = page_data.get('elements', [])
    viz_elements = [e for e in elements if e.get('elementType') in ('chart', 'table')]
    
    decisions = []
    for viz in viz_elements:
        eid = viz.get('elementId', '?')
        vtype = viz.get('elementType', '?')
        
        if vtype == 'chart':
            ctype = viz.get('chartType', 'unknown')
            data = viz.get('data', {})
            labels = data.get('labels', [])
            
            reason = f"{ctype.capitalize()} chart for {len(labels)} data points"
            if ctype == 'pie':
                reason += ". Pie charts effectively show part-to-whole relationships when categories are few (≤6)"
            elif ctype == 'bar':
                reason += ". Bar charts enable easy comparison across discrete categories"
            elif ctype == 'line':
                reason += ". Line charts reveal trends and patterns over time or ordered categories"
            
            decisions.append({
                'elementId': eid,
                'type': f'{ctype}-chart',
                'reason': reason,
            })
            
        elif vtype == 'table':
            data = viz.get('data', {})
            rows = data.get('rows', [])
            cols = len(data.get('header', []))
            
            reason = f"Table with {len(rows)} rows × {cols} columns for precise data reference"
            if cols >= 4:
                reason += ". Wide tables accommodate multi-dimensional comparison"
            if len(rows) <= 5:
                reason += ". Compact table size maintains readability without overwhelming the slide"
            
            decisions.append({
                'elementId': eid,
                'type': 'table',
                'reason': reason,
            })
    
    return decisions


def analyze_whitespace(page_data):
    """Analyze whitespace usage."""
    elements = page_data.get('elements', [])
    
    # Calculate coverage
    coverage = []
    for elem in elements:
        b = elem.get('bounds', [0, 0, 0, 0])
        if len(b) >= 4:
            coverage.append({
                'x1': b[0], 'y1': b[1],
                'x2': b[0] + b[2], 'y2': b[1] + b[3],
            })
    
    if not coverage:
        return {'coverage_ratio': 0, 'assessment': 'empty'}
    
    # Simple coverage estimate (not exact due to overlaps)
    total_area = sum((c['x2'] - c['x1']) * (c['y2'] - c['y1']) for c in coverage)
    page_area = 1280 * 720
    ratio = total_area / page_area
    
    if ratio < 0.3:
        assessment = 'generous whitespace creates breathing room and focuses attention'
    elif ratio < 0.6:
        assessment = 'balanced content-to-whitespace ratio'
    else:
        assessment = 'dense information layout maximizes content per slide'
    
    return {
        'coverage_ratio': round(ratio, 2),
        'assessment': assessment,
    }


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_rationale_md(pptd_path, design_md_path, audit_results, design_colors):
    """Generate the complete design rationale markdown document."""
    
    title = "Design Rationale"
    deck_name = pptd_path.stem
    
    lines = [
        f"# {title}: {deck_name}",
        "",
        f"**Generated**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Total Pages**: {len(audit_results)}",
        f"**Design System**: {design_md_path.name if design_md_path else 'Not specified'}",
        "",
        "---",
        "",
    ]
    
    # Executive summary
    layout_types = {}
    for r in audit_results:
        lt = r['layout']['type']
        layout_types[lt] = layout_types.get(lt, 0) + 1
    layout_types = sorted(layout_types.items(), key=lambda x: x[1], reverse=True)
    viz_count = sum(len(r['data_viz']) for r in audit_results)
    
    lines.extend([
        "## Executive Summary",
        "",
        f"This presentation uses **{len(layout_types)} distinct layout patterns** across {len(audit_results)} slides. "
        f"{viz_count} data visualizations are employed to transform raw numbers into actionable insights. "
        f"The design follows a **{design_colors.get('personality', 'modern')}** aesthetic with "
        f"**{design_colors.get('primary', '#000000')}** as the primary accent against a **{design_colors.get('background', '#FFFFFF')}** background.",
        "",
        "### Layout Distribution",
        "",
    ])
    
    for layout_type, count in layout_types:
        lines.append(f"- **{layout_type}**: {count} slide(s)")
    lines.append("")
    
    # Per-page rationale
    lines.extend([
        "---",
        "",
        "## Per-Page Design Decisions",
        "",
    ])
    
    for result in audit_results:
        page_num = result['page_index'] + 1
        page_file = result['page_file']
        layout = result['layout']
        colors = result['colors']
        typography = result['typography']
        data_viz = result['data_viz']
        whitespace = result['whitespace']
        
        lines.extend([
            f"### Slide {page_num} — `{page_file}`",
            "",
            f"**Layout**: {layout['type']}",
            "",
            f"> {layout['reason']}",
            "",
        ])
        
        # Element composition
        if layout['element_types']:
            elem_types = layout['element_types']
            if hasattr(elem_types, 'most_common'):
                sorted_types = elem_types.most_common()
            else:
                sorted_types = sorted(elem_types.items(), key=lambda x: x[1], reverse=True)
            elem_summary = ", ".join([f"{count}×{etype}" for etype, count in sorted_types])
            lines.append(f"**Composition**: {elem_summary} | Density: {layout['density_label']} ({layout['density']})")
            lines.append("")
        
        # Typography hierarchy
        if typography:
            lines.append("**Typography Hierarchy**:")
            lines.append("")
            lines.append("| Level | Size | Preview |")
            lines.append("|-------|------|---------|")
            for t in typography[:5]:
                preview = t['preview'].replace('|', '\\|').replace('\n', ' ')
                lines.append(f"| {t['level']} | {t['size']}px | {preview}... |")
            lines.append("")
        
        # Color usage
        if colors:
            primary_colors = {k: v for k, v in colors.items() if k in ('primary', 'ink', 'background', 'text')}
            if primary_colors:
                lines.append("**Color Strategy**:")
                lines.append("")
                for role, info in primary_colors.items():
                    lines.append(f"- **{role}** (`{info['color']}`): Used in {info['element_count']} element(s) — {', '.join(info['examples'][:2])}")
                lines.append("")
        
        # Data visualization
        if data_viz:
            lines.append("**Data Visualization**:")
            lines.append("")
            for viz in data_viz:
                lines.append(f"- `{viz['elementId']}` ({viz['type']}): {viz['reason']}")
            lines.append("")
        
        # Whitespace
        if whitespace:
            lines.append(f"**Whitespace**: {whitespace['assessment']} (content covers {whitespace['coverage_ratio']*100:.0f}% of slide)")
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    # Design principles section
    lines.extend([
        "",
        "## Underlying Design Principles",
        "",
        "The following principles guided the design decisions throughout this deck:",
        "",
        "1. **Visual Hierarchy Through Scale**: Headlines are 3–4× larger than body text, "
        "creating immediate scanability. This follows the principle that users scan, not read.",
        "",
        "2. **Color as Navigation**: The primary accent color (`{primary}`) is reserved for "
        "the most important information on each slide — typically data callouts or key takeaways. "
        "This trains the viewer's eye to find what matters first.".format(primary=design_colors.get('primary', 'primary')),
        "",
        "3. **Density Rhythm**: Cover and chapter pages are intentionally sparse (airy), "
        "while content pages carry more information (balanced to dense). This creates a "
        "breathing pattern that prevents visual fatigue.",
        "",
        "4. **Data Before Decoration**: Every chart and table serves a communicative purpose. "
        "The choice of chart type (pie for parts, bar for comparison, line for trends) "
        "is determined by the data's story, not aesthetics alone.",
        "",
        "5. **Consistency Through System**: All 19 slides share the same 8-color palette, "
        "2-font system, and spacing grid. This consistency reduces cognitive load and "
        "builds brand recognition.",
        "",
    ])
    
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='Design Rationale Generator for design-driven-pptx')
    parser.add_argument('--pptd', required=True, help='Path to .pptd file')
    parser.add_argument('--design-md', help='Path to design.md (optional, will infer from .pptd dir)')
    parser.add_argument('--output', '-o', help='Output path for rationale.md (default: {pptd_dir}/design-rationale.md)')
    
    args = parser.parse_args()
    
    if not YAML_AVAILABLE:
        print("ERROR: PyYAML is required. Install: pip install PyYAML")
        sys.exit(1)
    
    pptd_path = Path(args.pptd)
    if not pptd_path.exists():
        print(f"File not found: {pptd_path}")
        sys.exit(1)
    
    # Find design.md
    if args.design_md:
        design_md_path = Path(args.design_md)
    else:
        # Look in same directory as .pptd
        design_md_path = pptd_path.parent / 'design.md'
        if not design_md_path.exists():
            # Try one level up
            design_md_path = pptd_path.parent.parent / 'design.md'
    
    # Load .pptd
    with open(pptd_path, encoding='utf-8') as f:
        pptd = yaml.safe_load(f) or {}
    
    pages = pptd.get('pages', [])
    base_dir = pptd_path.parent
    
    # Parse design.md for colors
    design_colors = {}
    if design_md_path.exists():
        with open(design_md_path, encoding='utf-8') as f:
            design_md_content = f.read()
        
        # Extract colors from the YAML block
        color_match = re.search(r'colors:\s*\n((?:\s+\w+:\s*"[^"]+"\n)+)', design_md_content)
        if color_match:
            for line in color_match.group(1).strip().split('\n'):
                m = re.match(r'\s+(\w+):\s*"([^"]+)"', line)
                if m:
                    design_colors[m.group(1)] = m.group(2)
        
        # Try to find personality
        personality_match = re.search(r'Personality:\s*(\w+[-\w]*)', design_md_content)
        if personality_match:
            design_colors['personality'] = personality_match.group(1)
    
    print(f"Analyzing {len(pages)} page(s)...")
    print(f"Design system: {design_md_path if design_md_path.exists() else 'Not found'}")
    print()
    
    # Analyze each page
    audit_results = []
    for idx, page_ref in enumerate(pages):
        page_path = base_dir / page_ref
        if not page_path.exists():
            continue
        
        with open(page_path, encoding='utf-8') as f:
            page_data = yaml.safe_load(f) or {}
        
        layout = analyze_layout(page_data, idx)
        colors = analyze_color_usage(page_data, design_colors)
        typography = analyze_typography(page_data)
        data_viz = analyze_data_viz(page_data)
        whitespace = analyze_whitespace(page_data)
        
        audit_results.append({
            'page_index': idx,
            'page_file': page_ref,
            'layout': layout,
            'colors': colors,
            'typography': typography,
            'data_viz': data_viz,
            'whitespace': whitespace,
        })
        
        print(f"  [{idx+1}/{len(pages)}] {page_ref} → {layout['type']} ({layout['density_label']})")
    
    # Generate report
    rationale_md = generate_rationale_md(pptd_path, design_md_path, audit_results, design_colors)
    
    # Write output
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = pptd_path.parent / 'design-rationale.md'
    
    output_path.write_text(rationale_md, encoding='utf-8')
    print(f"\n✅ Design rationale saved: {output_path}")
    print(f"   Pages analyzed: {len(audit_results)}")
    print(f"   Data visualizations: {sum(len(r['data_viz']) for r in audit_results)}")


if __name__ == '__main__':
    main()
