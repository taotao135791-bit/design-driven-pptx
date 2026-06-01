#!/usr/bin/env python3
"""
Auto-Align — Snap all elements to a professional layout grid.

Usage:
    python auto_align.py <pptd_file> [--grid 8|12] [--verbose]

Grid systems:
    - 12-column grid for maximum compositional flexibility
    - 8px baseline grid for vertical rhythm
    - Golden ratio (φ ≈ 1.618) split options for asymmetric layouts
    - Fibonacci-based spacing scale for breathing room

Professional layout principles:
    - Page margin: 60px (generous but not wasteful)
    - Content width: 1160px (1280 - 60*2)
    - Gutter: 24px (slightly wider than default for breathing room)
    - Card internal padding: 24-32px (generous for modern feel)
    - Baseline: 8px (y positions snap to multiples of 8)
    - Fibonacci spacing: 8, 13, 21, 34, 55, 89px (for intentional whitespace)
"""

import sys
import argparse
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Grid Configuration
# ---------------------------------------------------------------------------

GRID = {
    'margin': 60,
    'gutter': 24,
    'card_padding': 24,
    'baseline': 8,
    'page_w': 1280,
    'page_h': 720,
}

# 12-column grid: each column = (1160 - 11*24) / 12 = 74.33... → snap to 74
# With 24px gutters, column widths work out to clean numbers
TWELVE_COL = {
    'col_w': 74,      # 12 cols × 74 = 888; with 11 gutters × 24 = 264; total = 1152
    'gutter': 24,
    'total': 1152,    # 888 + 264 = 1152 (slightly less than 1160, centered)
    'offset': 64,     # (1280 - 1152) / 2 = 64 — slight adjustment from 60 for centering
}

# Fibonacci spacing scale for intentional whitespace
FIBONACCI_SPACING = [8, 13, 21, 34, 55, 89]

# Golden ratio
PHI = 1.618033988749895

# ---------------------------------------------------------------------------
# Standard Column Layouts (precise pixel positions for 1280×720)
# ---------------------------------------------------------------------------

COLUMN_LAYOUTS = {
    1:  [(60, 1160)],
    2:  [(60, 560), (660, 560)],       # 60 + 560 + 40(gutter) + 560 + 60 = 1280
    3:  [(60, 360), (460, 360), (860, 360)],  # 60+360+40+360+40+360+60=1280
    4:  [(60, 260), (360, 260), (660, 260), (960, 260)],  # 60+260+40+260+40+260+40+260+60=1280
}

# Golden ratio splits
GOLDEN_SPLITS = {
    'left_minor':   (60, 436),     # 38.2% of 1160 = 443 → round to 436 for clean grid
    'left_major':   (60, 716),     # 61.8% of 1160 = 717 → round to 716
    'right_minor':  (784, 436),    # mirror of left_minor
    'right_major':  (504, 716),    # mirror of left_major
}

# Standard x positions for snapping (all column edges + card inner positions)
STD_X_POSITIONS = sorted(set([
    0, 60, 360, 460, 660, 784, 860, 960, 1220, 1280,  # page edges + column edges
    # Card content positions (card_x + padding)
    84, 384, 484, 684, 808, 884, 984,
]))

# Standard y positions for snapping (page edges + common content zones)
STD_Y_POSITIONS = sorted(set([
    0, 60, 80, 100, 120, 140, 160, 180, 200,
    240, 280, 320, 360, 400, 440, 480, 520, 560, 600, 640, 660, 720,
]))

# Content zone presets (for common slide structures)
CONTENT_ZONES = {
    'title_area':     (60, 60, 1160, 80),     # y: 60-140
    'body_top':       (60, 160, 1160, 400),   # y: 160-560
    'body_full':      (60, 140, 1160, 520),   # y: 140-660
    'sidebar_right':  (860, 160, 360, 520),   # x: 860-1220
    'footer_area':    (60, 660, 1160, 40),    # y: 660-700
}


def snap_to_grid(val, grid_size=8):
    """Snap a value to nearest grid multiple."""
    return round(val / grid_size) * grid_size


def snap_to_fibonacci(val, tolerance=10):
    """Snap a spacing value to nearest Fibonacci number."""
    for fib in FIBONACCI_SPACING:
        if abs(val - fib) <= tolerance:
            return fib
    return val


def snap_x(x, tolerance=15):
    """Snap x to nearest standard position."""
    for std_x in STD_X_POSITIONS:
        if abs(x - std_x) <= tolerance:
            return std_x
    # Also snap to 12-column grid positions
    grid_start = TWELVE_COL['offset']
    col_w = TWELVE_COL['col_w']
    gutter = TWELVE_COL['gutter']
    for i in range(13):
        pos = grid_start + i * (col_w + gutter)
        if abs(x - pos) <= tolerance:
            return pos
    return snap_to_grid(x, 8)


def snap_y(y, tolerance=12):
    """Snap y to nearest standard position or baseline grid."""
    for std_y in STD_Y_POSITIONS:
        if abs(y - std_y) <= tolerance:
            return std_y
    return snap_to_grid(y, 8)


def snap_width(w, tolerance=20):
    """Snap width to standard column widths or Fibonacci spacing."""
    std_widths = [260, 360, 560, 716, 436, 1160]
    for sw in std_widths:
        if abs(w - sw) <= tolerance:
            return sw
    return snap_to_grid(w, 8)


def snap_height(h, tolerance=20):
    """Snap height to standard content zone heights or baseline grid."""
    std_heights = [80, 160, 200, 240, 320, 400, 480, 520, 560]
    for sh in std_heights:
        if abs(h - sh) <= tolerance:
            return sh
    return snap_to_grid(h, 8)


def align_element(elem, verbose=False):
    """Snap a single element's bounds to the grid."""
    bounds = elem.get('bounds', [0, 0, 100, 100])
    if len(bounds) != 4:
        return elem

    x, y, w, h = bounds
    new_x = snap_x(x)
    new_y = snap_y(y)
    new_w = snap_width(w)
    new_h = snap_height(h)

    # Ensure element stays within page bounds
    if new_x + new_w > GRID['page_w']:
        new_w = GRID['page_w'] - new_x
    if new_y + new_h > GRID['page_h']:
        new_h = GRID['page_h'] - new_y

    if verbose and (new_x != x or new_y != y or new_w != w or new_h != h):
        print(f"  {elem.get('elementId', '?')}: [{x},{y},{w},{h}] → [{new_x},{new_y},{new_w},{new_h}]")

    elem['bounds'] = [new_x, new_y, new_w, new_h]
    return elem


def process_page(page, verbose=False):
    """Align all elements in a page."""
    elements = page.get('elements', [])
    for elem in elements:
        align_element(elem, verbose)
    page['elements'] = elements
    return page


def main():
    parser = argparse.ArgumentParser(description="Auto-align PPTD elements to professional grid")
    parser.add_argument("pptd", help="Path to .pptd master file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show alignment changes")
    parser.add_argument("--grid", type=int, choices=[8, 12], default=8, help="Grid size (default: 8px)")
    args = parser.parse_args()

    pptd_path = Path(args.pptd)
    if not pptd_path.exists():
        print(f"Error: file not found: {pptd_path}")
        sys.exit(1)

    # Load master
    with open(pptd_path, 'r', encoding='utf-8') as f:
        master = yaml.safe_load(f)

    pages = master.get('pages', [])
    if not pages:
        print("No pages found in master file")
        sys.exit(0)

    modified = 0
    for page_ref in pages:
        page_path = pptd_path.parent / page_ref
        if not page_path.exists():
            print(f"  Warning: page not found: {page_path}")
            continue

        with open(page_path, 'r', encoding='utf-8') as f:
            page = yaml.safe_load(f)

        if args.verbose:
            print(f"\nProcessing: {page_ref}")

        page = process_page(page, args.verbose)

        with open(page_path, 'w', encoding='utf-8') as f:
            yaml.dump(page, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

        modified += 1

    print(f"\nAligned {modified} page(s)")


if __name__ == "__main__":
    main()
