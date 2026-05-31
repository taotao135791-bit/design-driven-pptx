#!/usr/bin/env python3
"""
Drop-in replacement for runtime/kimi_pptd check.
Validates .pptd master and .page files.
"""

import argparse
import html
import os
import re
import sys
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DEFAULT_CANVAS = (1280, 720)
PAGE_TYPES = {"cover", "table_of_contents", "chapter", "content", "final"}

# Known shape names from the spec
KNOWN_SHAPES = {
    "rect",
    "roundRect",
    "ellipse",
    "triangle",
    "diamond",
    "plus",
    "star5",
    "rightArrow",
    "homePlate",
    "chevron",
    "donut",
    "flowChartProcess",
    "flowChartDecision",
    "flowChartTerminator",
    "straightConnector1",
    "bentConnector2",
    "bentConnector3",
    "bentConnector4",
    "curvedConnector2",
    "curvedConnector3",
    "curvedConnector4",
    "custom",
}

# Add all MSO_SHAPE names from python-pptx if available
try:
    from pptx.enum.shapes import MSO_SHAPE

    KNOWN_SHAPES.update(
        name for name in dir(MSO_SHAPE) if not name.startswith("_")
    )
except Exception:
    pass

# ---------------------------------------------------------------------------
# YAML helpers
# ---------------------------------------------------------------------------

def load_yaml(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def is_valid_color(value: str) -> bool:
    """Check if a color string is valid hex or $ref."""
    if not isinstance(value, str):
        return False
    if value.startswith("$"):
        return True
    if re.fullmatch(r"#[0-9A-Fa-f]{6}", value) or re.fullmatch(
        r"#[0-9A-Fa-f]{8}", value
    ):
        return True
    return False


def strip_html_tags(text: str) -> str:
    """Remove HTML tags and decode entities."""
    if not isinstance(text, str):
        return ""
    # Remove tags
    clean = re.sub(r"<[^>]+>", "", text)
    # Decode HTML entities
    clean = html.unescape(clean)
    return clean


def estimate_text_overflow(text: str, font_size: float, line_height_mult: float, wrap: bool, bounds_w: float, bounds_h: float):
    """
    Returns (overflow_ratio, details_str).
    overflow_ratio: negative or 0 means fits, positive means overflow percentage.
    """
    content = strip_html_tags(text)
    if not content:
        return (0.0, "empty text")

    # Count Chinese vs other chars
    chinese_chars = sum(1 for ch in content if "\u4e00" <= ch <= "\u9fff")
    other_chars = len(content) - chinese_chars

    total_width = chinese_chars * font_size + other_chars * font_size * 0.55

    if not wrap:
        if total_width <= bounds_w:
            return (0.0, "fits in one line")
        overflow = (total_width - bounds_w) / bounds_w if bounds_w > 0 else float("inf")
        return (overflow, f"width {total_width:.1f}px > bounds {bounds_w}px")

    # Wrapped mode
    if bounds_w <= 0:
        return (float("inf"), "zero width bounds")

    line_height = font_size * max(line_height_mult, 1.3)
    lines_needed = max(1, (total_width + bounds_w - 1) // bounds_w)  # ceil
    # Better ceil
    lines_needed = int((total_width + bounds_w - 1) // bounds_w)
    if lines_needed * bounds_w < total_width:
        lines_needed += 1

    total_height = lines_needed * line_height
    if total_height <= bounds_h:
        return (0.0, f"{lines_needed} lines fit")
    overflow = (total_height - bounds_h) / bounds_h if bounds_h > 0 else float("inf")
    return (overflow, f"{lines_needed} lines ({total_height:.1f}px) > bounds {bounds_h}px")


# ---------------------------------------------------------------------------
# Recursively find color strings and $refs in a nested dict/list
# ---------------------------------------------------------------------------

COLOR_FIELDS = {
    "color",
    "backgroundColor",
    "headerFill",
    "headerColor",
    "bodyFill",
    "bodyColor",
    "firstColumnFill",
    "firstColumnColor",
    "fill",
    "border",
    "shadow",
    "gradient",
    "stops",
    "mask",
    "arrow",
}

STYLE_FIELDS = {
    "style",
}


def collect_refs(obj, path=""):
    """Yield (field_path, value, context) for potential color/style refs."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_path = f"{path}.{k}" if path else k
            # Direct color fields
            if k in ("color", "backgroundColor", "headerColor", "bodyColor",
                     "firstColumnColor") and isinstance(v, str):
                yield (new_path, v, "color")
            elif k in ("headerFill", "firstColumnFill") and isinstance(v, str):
                yield (new_path, v, "color")
            elif k == "style" and isinstance(v, str):
                yield (new_path, v, "style")
            elif k == "bodyFill" and isinstance(v, list):
                for idx, item in enumerate(v):
                    if isinstance(item, str):
                        yield (f"{new_path}[{idx}]", item, "color")
            elif k == "colors" and isinstance(v, list):
                for idx, item in enumerate(v):
                    if isinstance(item, str):
                        yield (f"{new_path}[{idx}]", item, "color")
            else:
                yield from collect_refs(v, new_path)
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            new_path = f"{path}[{idx}]"
            if isinstance(item, str) and path.endswith(".stops"):
                # gradient stops can have color ref
                yield (new_path, item, "color")
            else:
                yield from collect_refs(item, new_path)


# ---------------------------------------------------------------------------
# Main checker
# ---------------------------------------------------------------------------

class Checker:
    def __init__(self, pptd_path: Path, pages_filter: set[str] | None = None):
        self.pptd_path = pptd_path
        self.base_dir = pptd_path.parent
        self.pages_filter = pages_filter
        self.canvas_w, self.canvas_h = DEFAULT_CANVAS
        self.theme_colors: dict = {}
        self.theme_text_styles: dict = {}
        self.theme_table_styles: dict = {}
        self.errors = 0
        self.warnings = 0

    def log(self, page: str, level: str, message: str):
        prefix = f"  [{level}]"
        print(f"{prefix} {message}")
        if level == "ERROR":
            self.errors += 1
        elif level == "WARNING":
            self.warnings += 1

    def run(self) -> int:
        print(f"=== Checking {self.pptd_path} ===")

        # 1. Load master
        try:
            master = load_yaml(self.pptd_path)
        except Exception as e:
            print(f"  [ERROR] Failed to parse {self.pptd_path}: {e}")
            self.errors += 1
            print(f"\nSummary: {self.errors} errors, {self.warnings} warnings")
            return 1

        if not isinstance(master, dict):
            print(f"  [ERROR] {self.pptd_path} is not a valid YAML mapping")
            self.errors += 1
            print(f"\nSummary: {self.errors} errors, {self.warnings} warnings")
            return 1

        # Canvas size
        size = master.get("size")
        if isinstance(size, (list, tuple)) and len(size) >= 2:
            self.canvas_w, self.canvas_h = float(size[0]), float(size[1])

        # Theme
        theme = master.get("theme") or {}
        self.theme_colors = (theme.get("colors") or {}) if isinstance(theme, dict) else {}
        self.theme_text_styles = (theme.get("textStyles") or {}) if isinstance(theme, dict) else {}
        self.theme_table_styles = (theme.get("tableStyles") or {}) if isinstance(theme, dict) else {}

        # Also validate theme color values
        for key, val in self.theme_colors.items():
            if isinstance(val, str) and not is_valid_color(val):
                print(f"  [ERROR] Invalid theme color '{key}': '{val}'")
                self.errors += 1

        pages = master.get("pages") or []
        if not isinstance(pages, list):
            print(f"  [ERROR] 'pages' must be an array")
            self.errors += 1
            print(f"\nSummary: {self.errors} errors, {self.warnings} warnings")
            return 1

        if self.pages_filter is not None:
            pages = [p for p in pages if p in self.pages_filter]

        for page_ref in pages:
            self.check_page(page_ref)

        print(f"\nSummary: {self.errors} errors, {self.warnings} warnings")
        return 1 if self.errors > 0 else 0

    def check_page(self, page_ref: str):
        page_path = self.base_dir / page_ref
        print(f"Page: {page_ref}")

        try:
            data = load_yaml(page_path)
        except Exception as e:
            self.log(page_ref, "ERROR", f"Failed to parse {page_ref}: {e}")
            return

        if not isinstance(data, dict):
            self.log(page_ref, "ERROR", f"{page_ref} is not a valid YAML mapping")
            return

        # Required fields
        page_type = data.get("pageType")
        if page_type not in PAGE_TYPES:
            self.log(
                page_ref,
                "ERROR",
                f"Invalid or missing pageType: {page_type!r} (expected one of {PAGE_TYPES})",
            )

        elements = data.get("elements")
        if not isinstance(elements, list):
            self.log(page_ref, "ERROR", "Missing or invalid 'elements' array")
            return

        seen_ids = set()
        for idx, elem in enumerate(elements):
            if not isinstance(elem, dict):
                self.log(page_ref, "ERROR", f"Element {idx} is not a mapping")
                continue
            self.check_element(page_ref, elem, idx, seen_ids)

    def check_element(self, page_ref: str, elem: dict, idx: int, seen_ids: set):
        eid = elem.get("elementId", f"<missing-id-{idx}>")

        if eid in seen_ids:
            self.log(page_ref, "ERROR", f'Duplicate elementId: "{eid}"')
        else:
            seen_ids.add(eid)

        # Bounds
        bounds = elem.get("bounds")
        if isinstance(bounds, (list, tuple)) and len(bounds) == 4:
            x, y, w, h = [float(v) for v in bounds]
            if w < 0 or h < 0:
                self.log(page_ref, "ERROR", f'element "{eid}" has negative width/height')
            else:
                # Check outside canvas
                fully_outside = (
                    x + w <= 0 or x >= self.canvas_w or y + h <= 0 or y >= self.canvas_h
                )
                partially_outside = (
                    x < -1 or y < -1 or x + w > self.canvas_w + 1 or y + h > self.canvas_h + 1
                )
                if fully_outside:
                    self.log(
                        page_ref,
                        "ERROR",
                        f'element "{eid}" bounds [{x},{y},{w},{h}] fully outside canvas',
                    )
                elif partially_outside:
                    self.log(
                        page_ref,
                        "WARNING",
                        f'element "{eid}" bounds extend outside canvas',
                    )
        else:
            self.log(page_ref, "ERROR", f'element "{eid}" missing or invalid bounds')

        # Layer
        if "layer" not in elem:
            self.log(
                page_ref, "WARNING", f'Missing layer field: element "{eid}"'
            )

        # Type-specific checks
        etype = elem.get("elementType")
        if etype == "text":
            self.check_text_element(page_ref, eid, elem)
        elif etype == "shape":
            self.check_shape_element(page_ref, eid, elem)

        # Color / ref validation across element
        self.check_colors_and_refs(page_ref, eid, elem)

    def check_text_element(self, page_ref: str, eid: str, elem: dict):
        content = elem.get("content") or {}
        if not isinstance(content, dict):
            self.log(page_ref, "ERROR", f'element "{eid}" content is not a mapping')
            return

        text = content.get("text", "")
        if not isinstance(text, str):
            text = str(text) if text is not None else ""

        # Resolve fontSize / lineHeight / wrap from content or theme style ref
        style_ref = content.get("style")
        resolved_style = {}
        if isinstance(style_ref, str) and style_ref.startswith("$"):
            key = style_ref[1:]
            resolved_style = self.theme_text_styles.get(key) or {}
            # Unknown style refs are reported by check_colors_and_refs
        elif isinstance(style_ref, dict):
            resolved_style = style_ref

        font_size = content.get("fontSize")
        if font_size is None:
            font_size = resolved_style.get("fontSize")
        if font_size is None:
            font_size = 18.0
        else:
            font_size = float(font_size)

        line_height = content.get("lineHeight")
        if line_height is None:
            line_height = resolved_style.get("lineHeight")
        if line_height is None:
            line_height = 1.0
        else:
            line_height = float(line_height)

        wrap = content.get("wrap")
        if wrap is None:
            wrap = True
        else:
            wrap = bool(wrap)

        bounds = elem.get("bounds")
        if isinstance(bounds, (list, tuple)) and len(bounds) == 4:
            bw, bh = float(bounds[2]), float(bounds[3])
            overflow_ratio, detail = estimate_text_overflow(
                text, font_size, line_height, wrap, bw, bh
            )
            if overflow_ratio > 0.10:
                pct = int(overflow_ratio * 100)
                self.log(
                    page_ref,
                    "WARNING",
                    f'Text overflow: element "{eid}" estimated {pct}% overflow ({detail})',
                )

    def check_shape_element(self, page_ref: str, eid: str, elem: dict):
        shape_name = elem.get("shapeName")
        if shape_name is None:
            self.log(page_ref, "ERROR", f'element "{eid}" missing shapeName')
            return
        if shape_name not in KNOWN_SHAPES:
            self.log(
                page_ref,
                "ERROR",
                f'element "{eid}" unknown shapeName: "{shape_name}"',
            )

    def check_colors_and_refs(self, page_ref: str, eid: str, elem: dict):
        for field_path, value, context in collect_refs(elem):
            if context == "color":
                if not is_valid_color(value):
                    self.log(
                        page_ref,
                        "ERROR",
                        f'element "{eid}" invalid color at {field_path}: "{value}"',
                    )
                elif value.startswith("$"):
                    key = value[1:]
                    if key not in self.theme_colors:
                        self.log(
                            page_ref,
                            "ERROR",
                            f'element "{eid}" unknown color reference "{value}" at {field_path}',
                        )
            elif context == "style":
                if value.startswith("$"):
                    key = value[1:]
                    # Could be text style or table style
                    if key not in self.theme_text_styles and key not in self.theme_table_styles:
                        self.log(
                            page_ref,
                            "ERROR",
                            f'element "{eid}" unknown style reference "{value}" at {field_path}',
                        )


def parse_args():
    parser = argparse.ArgumentParser(description="Check PPTD files")
    parser.add_argument("pptd_file", help="Path to the .pptd master file")
    parser.add_argument(
        "--pages",
        dest="pages",
        default=None,
        help="Comma-separated list of page files to check",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    pptd_path = Path(args.pptd_file).resolve()

    if not pptd_path.exists():
        print(f"ERROR: File not found: {pptd_path}")
        sys.exit(1)

    pages_filter = None
    if args.pages:
        pages_filter = set(p.strip() for p in args.pages.split(","))

    checker = Checker(pptd_path, pages_filter)
    sys.exit(checker.run())


if __name__ == "__main__":
    main()
