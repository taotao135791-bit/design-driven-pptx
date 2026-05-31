#!/usr/bin/env python3
"""
Semantic Auto-Visualization — Analyze .pptd content and automatically
insert charts, tables, and timelines where data patterns are detected.

Usage:
    python auto_visualizer.py --pptd test_e2e_coral/dreamina.pptd
    python auto_visualizer.py --pptd test.pptd --output test_viz.pptd --mode enhance

Modes:
    replace   — Replace bullet-list text elements with charts/tables
    enhance   — Keep original text, add visualization alongside (default)
    suggest   — Only print suggestions without modifying files
"""

import sys
import os
import re
import argparse
import copy
from pathlib import Path
from collections import defaultdict

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


# ---------------------------------------------------------------------------
# Data pattern detectors
# ---------------------------------------------------------------------------

# Regex patterns for different data types
PATTERNS = {
    # Distribution: values with percentages or parts of a whole
    'distribution': [
        r'([\w\s]+)[：:]\s*([\d.,]+)\s*(?:万|K|M|亿)?\s*[（(](\d+(?:\.\d+)?)%[）)]',
        r'([\w\s]+)[：:]\s*(\d+(?:\.\d+)?)%',
        r'([\w\s]+)\s+([\d.,]+)\s*(?:万|K|M|亿)?\s*[（(](\d+(?:\.\d+)?)%[）)]',
    ],
    # Time series: time labels with values
    'time_series': [
        r'(Q[1-4]|\d{4}年?|[一二三四五六七八九十]+月|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[：:]\s*([\d.,]+)',
        r'(第[一二三四五六七八九十\d]+[季度月周])\s*[：:]\s*([\d.,]+)',
    ],
    # Comparison: labeled values without time or percentage context
    'comparison': [
        r'([\w\s]+)[：:]\s*\$?([\d.,]+)\s*(?:万|K|M|亿|次|人|个|%)?',
        r'([\w\s]+)\s*([\d.,]+)\s*(?:万|K|M|亿|次|人|个)',
    ],
    # Sequential process: step/phase markers
    'sequential': [
        r'(?:步骤|Step|Phase|阶段|Step)\s*([\d一二三四五六七八九十]+)[：:.\s]+(.+)',
        r'([Qq][1-4]\s*期?)[:.\s]+(.+)',
        r'(第[一二三四五六七八九十\d]+步|阶段[一二三四五六七八九十\d])[:.\s]+(.+)',
    ],
}


def detect_data_type(text):
    """Analyze text and detect if it contains structured data.
    Returns: (data_type, extracted_data) or (None, None)
    """
    text = text.strip()
    if not text or len(text) < 20:
        return None, None
    
    lines = [l.strip() for l in text.split('\n') if l.strip() and not l.strip().startswith('•')]
    if not lines:
        lines = [l.strip('•- ') for l in text.split('\n') if l.strip()]
    
    # Detection order: most specific → most general
    # 1. Sequential (Step/Phase markers - strongest signal)
    seq_data = try_parse_sequential(lines)
    if seq_data and len(seq_data) >= 2:
        return 'sequential', seq_data
    
    # 2. Time series (Q1-Q4, Jan-Dec, etc.)
    ts_data = try_parse_time_series(lines)
    if ts_data and len(ts_data) >= 2:
        return 'time_series', ts_data
    
    # 3. Distribution (percentages that sum to ~100)
    dist_data = try_parse_distribution(lines)
    if dist_data and len(dist_data) >= 2:
        # Verify it looks like a real distribution (has percentages or sums reasonably)
        has_pcts = any(d.get('percentage') for d in dist_data)
        if has_pcts:
            return 'distribution', dist_data
        # Without percentages, might be comparison
    
    # 4. Comparison (any labeled values)
    comp_data = try_parse_comparison(lines)
    if comp_data and len(comp_data) >= 2:
        return 'comparison', comp_data
    
    # Fallback: distribution without percentages
    if dist_data and len(dist_data) >= 2:
        return 'distribution', dist_data
    
    return None, None


def try_parse_distribution(lines):
    """Parse distribution data: label + value + optional percentage."""
    results = []
    for line in lines:
        line = line.strip('•- ')
        # Skip lines that look like steps/phases (have Step/Phase/步骤 in them)
        if re.search(r'(?:步骤|Step|Phase|阶段|第[一二三四五六七八九十\d]+步)\s*\d+', line, re.I):
            continue
        # Match patterns like "UAC $80K（60%）" or "UAC: 80万(60%)"
        m = re.search(r'([\w\s/]+?)[：:\s]+\$?([\d.,]+)\s*(?:万|K|M|亿)?\s*(?:[（(](\d+(?:\.\d+)?)%[）)]|)', line)
        if m:
            label = m.group(1).strip()
            value = float(m.group(2).replace(',', ''))
            pct = float(m.group(3)) if m.group(3) else None
            # Reject if label looks like a step number
            if re.match(r'^\d+$', label):
                continue
            results.append({'label': label, 'value': value, 'percentage': pct})
    return results if len(results) >= 2 else None


def try_parse_time_series(lines):
    """Parse time series data: time label + value."""
    results = []
    time_pattern = re.compile(r'(Q[1-4]|\d{4}年?|[一二三四五六七八九十]+月|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|第[一二三四五六七八九十\d]+[季度月周])')
    
    for line in lines:
        line = line.strip('•- ')
        tm = time_pattern.search(line)
        if tm:
            time_label = tm.group(1)
            # Extract number after time label
            rest = line[tm.end():]
            vm = re.search(r'[：:\s]+\$?([\d.,]+)', rest)
            if vm:
                value = float(vm.group(1).replace(',', ''))
                results.append({'time': time_label, 'value': value})
    return results if len(results) >= 2 else None


def try_parse_comparison(lines):
    """Parse comparison data: label + numeric value."""
    results = []
    for line in lines:
        line = line.strip('•- ')
        # Skip lines that look like time series or have percentages
        if re.search(r'(Q[1-4]|\d{4}年|第[一二三四]季度)', line):
            continue
        m = re.search(r'([\w\s/]+?)[：:\s]+\$?([\d.,]+)\s*(?:万|K|M|亿|次|人|个|%)?', line)
        if m:
            label = m.group(1).strip()
            value = float(m.group(2).replace(',', ''))
            # Skip if it looks like a year or non-meaningful label
            if label and len(label) > 1 and not label.isdigit():
                results.append({'label': label, 'value': value})
    return results if len(results) >= 2 else None


def try_parse_sequential(lines):
    """Parse sequential process data: step number + description."""
    results = []
    for line in lines:
        line = line.strip('•- ')
        # Match "Step 1: description" or "步骤1：description" or "阶段一: description"
        m = re.search(r'(?:步骤|Step|Phase|阶段)\s*([\d一二三四五六七八九十]+)[：:.\s]+(.+)', line, re.I)
        if m:
            step = m.group(1)
            desc = m.group(2).strip()
            results.append({'step': step, 'description': desc})
            continue
        # Also match "1. description" or "(1) description" at start of line
        m2 = re.match(r'^(?:\(?)([\d一二三四五六七八九十]+)(?:\)?)[.\.、\s]+(.+)', line)
        if m2:
            step = m2.group(1)
            desc = m2.group(2).strip()
            results.append({'step': step, 'description': desc})
    return results if len(results) >= 2 else None


# ---------------------------------------------------------------------------
# Visualization builders
# ---------------------------------------------------------------------------

def build_pie_chart(data, bounds, element_id='auto-chart'):
    """Build a pie chart element from distribution data."""
    labels = [d['label'] for d in data]
    values = [d['value'] for d in data]
    
    return {
        'elementId': element_id,
        'elementType': 'chart',
        'bounds': bounds,
        'layer': 1,
        'chartType': 'pie',
        'data': {
            'labels': labels,
            'values': values,
        },
        'legend': {'position': 'right'},
    }


def build_bar_chart(data, bounds, element_id='auto-chart'):
    """Build a bar chart element from comparison data."""
    labels = [d['label'] for d in data]
    values = [d['value'] for d in data]
    
    return {
        'elementId': element_id,
        'elementType': 'chart',
        'bounds': bounds,
        'layer': 1,
        'chartType': 'bar',
        'data': {
            'labels': labels,
            'values': values,
        },
    }


def build_line_chart(data, bounds, element_id='auto-chart'):
    """Build a line chart element from time series data."""
    labels = [d['time'] for d in data]
    values = [d['value'] for d in data]
    
    return {
        'elementId': element_id,
        'elementType': 'chart',
        'bounds': bounds,
        'layer': 1,
        'chartType': 'line',
        'data': {
            'labels': labels,
            'values': values,
        },
        'seriesStyle': {'smooth': True},
    }


def build_table(data, bounds, element_id='auto-table', data_type='comparison'):
    """Build a table element from structured data."""
    if data_type == 'distribution':
        header = ['项目', '数值', '占比']
        rows = [[d['label'], str(d['value']), f"{d['percentage']}%" if d.get('percentage') else '-'] for d in data]
    elif data_type == 'time_series':
        header = ['时间', '数值']
        rows = [[d['time'], str(d['value'])] for d in data]
    else:
        header = ['项目', '数值']
        rows = [[d['label'], str(d['value'])] for d in data]
    
    return {
        'elementId': element_id,
        'elementType': 'table',
        'bounds': bounds,
        'layer': 1,
        'tableStyle': '$tableStyles.default',
        'data': {
            'header': header,
            'rows': rows,
        },
    }


def build_timeline_elements(data, start_y=200):
    """Build timeline elements (shapes + text) from sequential data."""
    elements = []
    y = start_y
    x_left = 100
    x_right = 500
    spacing = 120
    
    for i, item in enumerate(data):
        is_left = i % 2 == 0
        x = x_left if is_left else x_right
        
        # Node dot
        elements.append({
            'elementId': f'tl-node-{i}',
            'elementType': 'shape',
            'bounds': [340, y + 20, 20, 20],
            'shapeName': 'ellipse',
            'fill': {'type': 'solid', 'color': '$primary'},
            'layer': 1,
        })
        
        # Label
        elements.append({
            'elementId': f'tl-label-{i}',
            'elementType': 'text',
            'bounds': [x, y, 300, 30],
            'content': {
                'text': item['step'],
                'fontSize': 18,
                'color': '$primary',
                'fontFamily': 'Bebas Neue, ZCOOL XiaoWei',
            },
            'wrap': False,
            'layer': 1,
        })
        
        # Description
        elements.append({
            'elementId': f'tl-desc-{i}',
            'elementType': 'text',
            'bounds': [x, y + 35, 300, 60],
            'content': {
                'text': item['description'],
                'fontSize': 14,
                'color': '$text',
                'fontFamily': 'Inter, Yozai',
                'lineHeight': 1.5,
            },
            'layer': 1,
        })
        
        y += spacing
    
    # Vertical line
    elements.insert(0, {
        'elementId': 'tl-line',
        'elementType': 'shape',
        'bounds': [349, start_y, 2, (len(data) - 1) * spacing + 40],
        'shapeName': 'rect',
        'fill': {'type': 'solid', 'color': '$primary'},
        'opacity': 0.3,
        'layer': 0,
    })
    
    return elements


# ---------------------------------------------------------------------------
# Page processor
# ---------------------------------------------------------------------------

def calculate_viz_bounds(page_data, existing_elements, viz_type, mode='enhance'):
    """Calculate where to place the visualization on the page."""
    # Default full-page bounds
    page_w, page_h = 1280, 720
    
    if mode == 'replace':
        # Will replace text element, use its bounds
        return None
    
    # Find available space
    # Simple heuristic: if page has left-heavy content, put viz on right half
    has_left_content = False
    has_right_content = False
    for e in existing_elements:
        b = e.get('bounds', [0, 0, 0, 0])
        cx = b[0] + b[2] / 2
        if cx < page_w / 2:
            has_left_content = True
        else:
            has_right_content = True
    
    if viz_type == 'pie':
        if has_left_content and not has_right_content:
            return [680, 150, 540, 420]
        elif has_right_content and not has_left_content:
            return [60, 150, 540, 420]
        else:
            return [340, 360, 600, 320]
    elif viz_type == 'bar':
        if has_left_content and not has_right_content:
            return [680, 120, 540, 480]
        else:
            return [60, 360, 1160, 280]
    elif viz_type == 'line':
        return [60, 320, 1160, 320]
    else:
        return [60, 360, 1160, 280]


def process_page(page_path, mode='enhance'):
    """Process a single page file, detect data patterns, insert visualizations.
    Returns: (modified, suggestions, new_elements_count)
    """
    with open(page_path, encoding='utf-8') as f:
        page_data = yaml.safe_load(f) or {}
    
    elements = page_data.get('elements', [])
    suggestions = []
    new_elements = []
    modified = False
    
    for i, elem in enumerate(elements):
        if elem.get('elementType') != 'text':
            continue
        
        content = elem.get('content', {})
        text = content.get('text', '')
        if not text:
            continue
        
        data_type, data = detect_data_type(text)
        if not data_type:
            continue
        
        elem_id = elem.get('elementId', f'elem-{i}')
        suggestions.append({
            'elementId': elem_id,
            'dataType': data_type,
            'itemCount': len(data),
            'sample': str(data[0]) if data else None,
        })
        
        if mode == 'suggest':
            continue
        
        # Generate visualization
        if data_type == 'distribution':
            bounds = calculate_viz_bounds(page_data, elements, 'pie', mode)
            viz = build_pie_chart(data, bounds, f'viz-{elem_id}')
            new_elements.append(viz)
            
        elif data_type == 'time_series':
            bounds = calculate_viz_bounds(page_data, elements, 'line', mode)
            viz = build_line_chart(data, bounds, f'viz-{elem_id}')
            new_elements.append(viz)
            
        elif data_type == 'comparison':
            bounds = calculate_viz_bounds(page_data, elements, 'bar', mode)
            viz = build_bar_chart(data, bounds, f'viz-{elem_id}')
            new_elements.append(viz)
            
        elif data_type == 'sequential':
            # Timeline uses multiple elements
            timeline_elems = build_timeline_elements(data)
            new_elements.extend(timeline_elems)
        
        if mode == 'replace' and data_type != 'sequential':
            # Mark original element for reduction (make it smaller or caption)
            elem['bounds'][3] = 40  # Shrink to caption height
            if 'content' in elem:
                elem['content']['fontSize'] = min(elem['content'].get('fontSize', 18), 14)
        
        modified = True
    
    if new_elements and mode != 'suggest':
        # Insert new elements before page-level decorations
        insert_idx = len(elements)
        for idx, e in enumerate(elements):
            if e.get('elementId', '').startswith(('deco-', 'deco', 'hatch', 'bg-')):
                insert_idx = idx
                break
        
        for viz in new_elements:
            elements.insert(insert_idx, viz)
            insert_idx += 1
        
        page_data['elements'] = elements
        
        # Write back
        with open(page_path, 'w', encoding='utf-8') as f:
            yaml.dump(page_data, f, allow_unicode=True, sort_keys=False, width=200)
    
    return modified, suggestions, len(new_elements)


# ---------------------------------------------------------------------------
# Main CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='Semantic Auto-Visualization for design-driven-pptx')
    parser.add_argument('--pptd', required=True, help='Path to .pptd file')
    parser.add_argument('--output', help='Output .pptd path (default: in-place modify or append _viz)')
    parser.add_argument('--mode', choices=['replace', 'enhance', 'suggest'], default='enhance',
                        help='replace=swap text for charts, enhance=add alongside, suggest=preview only')
    parser.add_argument('--pages', help='Comma-separated page indices to process (1-based, default: all)')
    
    args = parser.parse_args()
    
    if not YAML_AVAILABLE:
        print("ERROR: PyYAML is required. Install: pip install PyYAML")
        sys.exit(1)
    
    pptd_path = Path(args.pptd)
    if not pptd_path.exists():
        print(f"File not found: {pptd_path}")
        sys.exit(1)
    
    # Load .pptd to get page list
    with open(pptd_path, encoding='utf-8') as f:
        pptd = yaml.safe_load(f) or {}
    
    pages = pptd.get('pages', [])
    base_dir = pptd_path.parent
    
    # Determine which pages to process
    if args.pages:
        page_indices = [int(x.strip()) - 1 for x in args.pages.split(',')]
    else:
        page_indices = list(range(len(pages)))
    
    # If output is specified and different from input, copy the whole directory first
    if args.output and Path(args.output).resolve() != pptd_path.resolve():
        import shutil
        out_dir = Path(args.output).parent
        if out_dir.exists():
            shutil.rmtree(out_dir)
        shutil.copytree(base_dir, out_dir)
        base_dir = out_dir
        pptd_path = out_dir / pptd_path.name
    
    print(f"Processing {len(page_indices)} page(s) in mode: {args.mode}")
    print("=" * 60)
    
    total_suggestions = 0
    total_added = 0
    
    for idx in page_indices:
        if idx < 0 or idx >= len(pages):
            continue
        
        page_ref = pages[idx]
        page_path = base_dir / page_ref
        
        if not page_path.exists():
            print(f"  [{idx+1}] SKIP (not found): {page_ref}")
            continue
        
        modified, suggestions, added = process_page(page_path, mode=args.mode)
        
        if suggestions:
            print(f"  [{idx+1}] {page_ref}")
            for s in suggestions:
                action = "→ would add" if args.mode == 'suggest' else "→ added"
                print(f"      {action} {s['dataType']} ({s['itemCount']} items) from element '{s['elementId']}'")
            total_suggestions += len(suggestions)
            total_added += added
    
    print("=" * 60)
    if args.mode == 'suggest':
        print(f"Found {total_suggestions} data visualization opportunity(s)")
        print("Run with --mode enhance to apply them")
    else:
        print(f"Added {total_added} visualization element(s) across {total_suggestions} opportunity(s)")
        print(f"Output: {pptd_path}")


if __name__ == '__main__':
    main()
