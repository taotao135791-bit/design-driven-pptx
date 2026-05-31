#!/usr/bin/env python3
"""
Auto-Align — Snap all elements to a unified spacing grid.

Usage:
    python auto_align.py <pptd_file>

Grid rules:
    - Page margin: 60px
    - Content width: 1160px (1280 - 60*2)
    - Gutter: 20px
    - Card internal padding: 20px
    - Standard column positions:
        1-col: [60, y, 1160, h]
        2-col: [60, y, 560, h] + [640, y, 560, h]
        3-col: [60, y, 360, h] + [440, y, 360, h] + [820, y, 360, h]
        4-col: [60, y, 270, h] + [350, y, 270, h] + [640, y, 270, h] + [930, y, 270, h]
    - Baseline: 8px (y positions snap to multiples of 8)
"""

import sys
import argparse
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml")
    sys.exit(1)

# Grid configuration
GRID = {
    'margin': 60,
    'gutter': 20,
    'card_padding': 20,
    'baseline': 8,
    'page_w': 1280,
}

# Standard column layouts (x positions and widths)
COLUMN_LAYOUTS = {
    1: [(60, 1160)],
    2: [(60, 560), (640, 560)],
    3: [(60, 360), (440, 360), (820, 360)],
    4: [(60, 270), (350, 270), (640, 270), (930, 270)],
}

# Standard x positions for snapping
STD_X_POSITIONS = [0, 60, 350, 440, 640, 820, 930, 640]
# Add card-content positions (card_x + padding)
for x, w in [(60,560),(640,560),(60,360),(440,360),(820,360),(60,270),(350,270),(640,270),(930,270)]:
    STD_X_POSITIONS.append(x + 20)
STD_X_POSITIONS = sorted(set(STD_X_POSITIONS))


def snap_to_grid(val, grid_size=8):
    """Snap a value to nearest grid multiple."""
    return round(val / grid_size) * grid_size


def snap_x(x, tolerance=15):
    """Snap x to nearest standard position."""
    for std_x in STD_X_POSITIONS:
        if abs(x - std_x) <= tolerance:
            return std_x
    # Also snap to margin + padding positions
    if abs(x - 80) <= tolerance:
        return 80
    if abs(x - 85) <= tolerance:
        return 80
    if abs(x - 90) <= tolerance:
        return 80
    if abs(x - 100) <= tolerance:
        return 100
    if abs(x - 120) <= tolerance:
        return 120
    if abs(x - 125) <= tolerance:
        return 120
    if abs(x - 130) <= tolerance:
        return 120
    if abs(x - 135) <= tolerance:
        return 120
    if abs(x - 380) <= tolerance:
        return 380
    if abs(x - 385) <= tolerance:
        return 380
    if abs(x - 390) <= tolerance:
        return 380
    if abs(x - 485) <= tolerance:
        return 480
    if abs(x - 525) <= tolerance:
        return 520
    if abs(x - 680) <= tolerance:
        return 680
    if abs(x - 685) <= tolerance:
        return 680
    if abs(x - 720) <= tolerance:
        return 720
    if abs(x - 740) <= tolerance:
        return 740
    if abs(x - 890) <= tolerance:
        return 890
    if abs(x - 985) <= tolerance:
        return 980
    if abs(x - 1020) <= tolerance:
        return 1020
    if abs(x - 1040) <= tolerance:
        return 1040
    return x


def snap_y(y, tolerance=10):
    """Snap y to baseline grid."""
    snapped = snap_to_grid(y, GRID['baseline'])
    if abs(y - snapped) <= tolerance:
        return snapped
    return y


def fix_card_padding(element, card_bounds):
    """Fix text element padding inside a card."""
    b = element.get('bounds', [])
    if len(b) < 4:
        return element
    
    cb = card_bounds
    # Check if element is inside card
    if b[0] >= cb[0] and b[0] + b[2] <= cb[0] + cb[2] and \
       b[1] >= cb[1] and b[1] + b[3] <= cb[1] + cb[3]:
        # Snap to card padding
        expected_x = cb[0] + 20
        expected_w = cb[2] - 40
        
        # Only adjust if close to expected
        if abs(b[0] - expected_x) <= 15:
            b[0] = expected_x
        if abs((b[0] + b[2]) - (cb[0] + cb[2] - 20)) <= 15:
            b[2] = cb[0] + cb[2] - 20 - b[0]
    
    return element


def detect_cards(elements):
    """Detect card shapes (rectangles with fill that likely contain other elements)."""
    cards = []
    for e in elements:
        if e.get('elementType') == 'shape' and e.get('shapeName') == 'rect':
            b = e.get('bounds', [])
            if len(b) >= 4:
                # Cards are typically >200px wide and >80px tall, not full-width
                if 200 < b[2] < 1200 and b[3] > 80:
                    # Check if it has a fill (not just a border)
                    fill = e.get('fill', {})
                    if fill and fill.get('type') == 'solid':
                        cards.append((e, b))
    return cards


def fix_overlaps(elements):
    """Fix overlapping text/shape elements by adjusting positions."""
    # Sort by y, then x
    sorted_elems = sorted(enumerate(elements), key=lambda x: (x[1].get('bounds', [0,0,0,0])[1], x[1].get('bounds', [0,0,0,0])[0]))
    
    for i, (idx1, e1) in enumerate(sorted_elems):
        b1 = e1.get('bounds', [])
        if len(b1) < 4:
            continue
        if e1.get('elementType') == 'shape' and e1.get('elementId', '').startswith(('bg-', 'hatch', 'deco')):
            continue  # Skip background/decorative shapes
        
        for j, (idx2, e2) in enumerate(sorted_elems):
            if i >= j:
                continue
            b2 = e2.get('bounds', [])
            if len(b2) < 4:
                continue
            if e2.get('elementType') == 'shape' and e2.get('elementId', '').startswith(('bg-', 'hatch', 'deco')):
                continue
            
            # Check overlap
            x1, y1, w1, h1 = b1
            x2, y2, w2, h2 = b2
            if x1 < x2+w2 and x1+w1 > x2 and y1 < y2+h2 and y1+h1 > y2:
                overlap_w = min(x1+w1, x2+w2) - max(x1, x2)
                overlap_h = min(y1+h1, y2+h2) - max(y1, y2)
                if overlap_w > 5 and overlap_h > 5:
                    # Move the lower element down
                    new_y = y2 + h1 + 10
                    b2[1] = new_y
                    print(f"    Fixed overlap: moved '{e2.get('elementId','?')}' y: {y2} -> {new_y}")
    
    return elements


def process_page(page_path):
    """Process a single page file."""
    with open(page_path, encoding='utf-8') as f:
        page_data = yaml.safe_load(f) or {}
    
    elements = page_data.get('elements', [])
    if not elements:
        return False
    
    print(f"\nProcessing: {page_path.name}")
    
    # Detect cards
    cards = detect_cards(elements)
    card_bounds = {e.get('elementId'): b for e, b in cards}
    
    fixes = []
    
    for element in elements:
        eid = element.get('elementId', '?')
        etype = element.get('elementType', '?')
        b = element.get('bounds', [])
        if len(b) < 4:
            continue
        
        original = list(b)
        
        # Snap x position
        if b[2] < 1200:  # Not full-width
            b[0] = snap_x(b[0])
        
        # Snap y position to baseline
        b[1] = snap_y(b[1])
        
        # Snap width to standard column widths
        for x, w in [(60,1160),(60,560),(640,560),(60,360),(440,360),(820,360),(60,270),(350,270),(640,270),(930,270)]:
            if abs(b[0] - x) <= 5 and abs(b[2] - w) <= 20:
                b[2] = w
                break
        
        # Fix card padding for text elements inside cards
        if etype == 'text':
            for cid, cb in card_bounds.items():
                if b[0] >= cb[0] and b[0] < cb[0] + cb[2] and \
                   b[1] >= cb[1] and b[1] < cb[1] + cb[3]:
                    fix_card_padding(element, cb)
                    break
        
        if original != b:
            fixes.append(f"  {eid}: bounds {original} -> {b}")
    
    # Fix overlaps
    elements = fix_overlaps(elements)
    
    if fixes:
        for f in fixes[:5]:
            print(f)
        if len(fixes) > 5:
            print(f"  ... and {len(fixes)-5} more fixes")
    else:
        print("  No alignment fixes needed")
    
    # Write back
    page_data['elements'] = elements
    with open(page_path, 'w', encoding='utf-8') as f:
        yaml.dump(page_data, f, allow_unicode=True, sort_keys=False, width=200)
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Auto-align PPTD elements to spacing grid')
    parser.add_argument('pptd', help='Path to .pptd file')
    args = parser.parse_args()
    
    pptd_path = Path(args.pptd)
    if not pptd_path.exists():
        print(f"File not found: {pptd_path}")
        sys.exit(1)
    
    with open(pptd_path, encoding='utf-8') as f:
        pptd = yaml.safe_load(f) or {}
    
    base_dir = pptd_path.parent
    pages = pptd.get('pages', [])
    
    print(f"Auto-aligning {len(pages)} page(s) to grid...")
    print(f"Grid: margin={GRID['margin']}, gutter={GRID['gutter']}, baseline={GRID['baseline']}")
    
    fixed = 0
    for page_ref in pages:
        page_path = base_dir / page_ref
        if page_path.exists():
            if process_page(page_path):
                fixed += 1
    
    print(f"\n✅ Done: {fixed} page(s) aligned")


if __name__ == '__main__':
    main()
