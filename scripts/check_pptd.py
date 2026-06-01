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
from typing import Optional

import yaml

# ---------------------------------------------------------------------------
# Color helpers (inline to avoid import path issues)
# ---------------------------------------------------------------------------
def _luminance(hex_color):
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
    g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
    b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DEFAULT_CANVAS = (1280, 720)
PAGE_TYPES = {"cover", "table_of_contents", "chapter", "content", "final"}

MINIMAL_STYLES = {"monochrome", "vellum", "cartesian"}

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

# Shapes that suggest a timeline / step node layout is present
TIMELINE_STEP_SHAPES = {
    "flowChartProcess",
    "flowChartDecision",
    "flowChartTerminator",
    "chevron",
    "homePlate",
    "straightConnector1",
    "bentConnector2",
    "bentConnector3",
    "bentConnector4",
    "curvedConnector2",
    "curvedConnector3",
    "curvedConnector4",
}

# Add all MSO_SHAPE names from python-pptx if available
try:
    from pptx.enum.shapes import MSO_SHAPE

    KNOWN_SHAPES.update(
        name for name in dir(MSO_SHAPE) if not name.startswith("_")
    )
except (ImportError, AttributeError):
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


def estimate_text_overflow(
    text: str,
    font_size: float,
    line_height_mult: float,
    wrap: bool,
    bounds_w: float,
    bounds_h: float,
):
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
        overflow = (
            (total_width - bounds_w) / bounds_w if bounds_w > 0 else float("inf")
        )
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
    overflow = (
        (total_height - bounds_h) / bounds_h if bounds_h > 0 else float("inf")
    )
    return (overflow, f"{lines_needed} lines ({total_height:.1f}px) > bounds {bounds_h}px")


# ---------------------------------------------------------------------------
# Data-visualization opportunity helpers
# ---------------------------------------------------------------------------


def count_bullet_items(text: str) -> int:
    """Count bullet list items in text (HTML <ul> or plain text bullets)."""
    if not isinstance(text, str):
        return 0
    count = 0
    # HTML unordered lists
    for ul_content in re.findall(r"(?i)<ul[^>]*>(.*?)</ul>", text, re.DOTALL):
        count += len(re.findall(r"(?i)<li(?:\s|>)", ul_content))

    # Plain text bullets from stripped text
    plain = strip_html_tags(text)
    for line in plain.splitlines():
        stripped = line.strip()
        if stripped.startswith("• ") or stripped.startswith("- "):
            count += 1
    return count


def count_numbered_steps(text: str) -> int:
    """Count numbered step items in text (HTML <ol> or plain text 1. 2. 3.)."""
    if not isinstance(text, str):
        return 0
    count = 0
    # HTML ordered lists
    for ol_content in re.findall(r"(?i)<ol[^>]*>(.*?)</ol>", text, re.DOTALL):
        count += len(re.findall(r"(?i)<li(?:\s|>)", ol_content))

    # Plain text numbered items from stripped text
    plain = strip_html_tags(text)
    for line in plain.splitlines():
        stripped = line.strip()
        if re.match(r"^\d+\.\s", stripped):
            count += 1
    return count


def has_chart_table_timeline(elements: list) -> bool:
    """Return True if page contains chart, table, or timeline-like elements."""
    for elem in elements:
        etype = elem.get("elementType")
        if etype in ("chart", "table"):
            return True
        if etype == "shape" and elem.get("shapeName") in TIMELINE_STEP_SHAPES:
            return True
    return False


def has_timeline_step_nodes(elements: list) -> bool:
    """Return True if page contains timeline or step node shapes."""
    for elem in elements:
        if (
            elem.get("elementType") == "shape"
            and elem.get("shapeName") in TIMELINE_STEP_SHAPES
        ):
            return True
    return False


# ---------------------------------------------------------------------------
# Card helpers
# ---------------------------------------------------------------------------


def is_card(elem: dict) -> bool:
    """Return True if element looks like a card shape."""
    if elem.get("elementType") != "shape":
        return False
    shape_name = elem.get("shapeName")
    if shape_name not in ("rect", "roundRect"):
        return False
    bounds = elem.get("bounds")
    if not isinstance(bounds, (list, tuple)) or len(bounds) != 4:
        return False
    w, h = float(bounds[2]), float(bounds[3])
    if w < 150 or h < 80:
        return False
    border = elem.get("border")
    if not isinstance(border, dict):
        return False
    if border.get("style") == "none":
        return False
    return True


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
            if (
                k
                in (
                    "color",
                    "backgroundColor",
                    "headerColor",
                    "bodyColor",
                    "firstColumnColor",
                )
                and isinstance(v, str)
            ):
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
    def __init__(self, pptd_path: Path, pages_filter: Optional[set[str]] = None):
        self.pptd_path = pptd_path
        self.base_dir = pptd_path.parent
        self.pages_filter = pages_filter
        self.canvas_w, self.canvas_h = DEFAULT_CANVAS
        self.theme_colors: dict = {}
        self.theme_text_styles: dict = {}
        self.theme_table_styles: dict = {}
        self.errors = 0
        self.warnings = 0
        self.cards_across_pages: list[tuple[str, float]] = []

    def log(self, page: str, level: str, message: str):
        prefix = f"  [{level}]"
        if page and page != "deck":
            print(f"{prefix} {message}")
        else:
            print(f"Deck: {prefix} {message}")
        if level == "ERROR":
            self.errors += 1
        elif level == "WARNING":
            self.warnings += 1

    def run(self) -> int:
        print(f"=== Checking {self.pptd_path} ===")

        # 1. Load master
        try:
            master = load_yaml(self.pptd_path)
        except (yaml.YAMLError, OSError, UnicodeDecodeError) as e:
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
        self.theme_colors = (
            (theme.get("colors") or {}) if isinstance(theme, dict) else {}
        )
        self.theme_text_styles = (
            (theme.get("textStyles") or {}) if isinstance(theme, dict) else {}
        )
        self.theme_table_styles = (
            (theme.get("tableStyles") or {}) if isinstance(theme, dict) else {}
        )

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

        # Cross-page checks
        self.check_card_consistency_across_pages()

        print(f"\nSummary: {self.errors} errors, {self.warnings} warnings")
        return 1 if self.errors > 0 else 0

    def check_page(self, page_ref: str):
        page_path = self.base_dir / page_ref
        print(f"Page: {page_ref}")

        try:
            data = load_yaml(page_path)
        except (yaml.YAMLError, OSError, UnicodeDecodeError) as e:
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
        valid_elements = []
        for idx, elem in enumerate(elements):
            if not isinstance(elem, dict):
                self.log(page_ref, "ERROR", f"Element {idx} is not a mapping")
                continue
            self.check_element(page_ref, elem, idx, seen_ids)
            valid_elements.append(elem)

        # New quality checks
        self.check_data_visualization_opportunity(
            page_ref, page_type, valid_elements
        )
        self.check_chart_annotations(page_ref, valid_elements)
        self.check_text_contrast(page_ref, valid_elements)
        self.check_layout_quality(page_ref, valid_elements)

        # Collect card info for cross-page consistency
        for elem in valid_elements:
            if is_card(elem):
                border = elem.get("border") or {}
                border_width = border.get("width", 1)
                if border_width is None:
                    border_width = 1
                self.cards_across_pages.append((page_ref, float(border_width)))

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
                self.log(
                    page_ref, "ERROR", f'element "{eid}" has negative width/height'
                )
            else:
                # Check outside canvas
                fully_outside = (
                    x + w <= 0
                    or x >= self.canvas_w
                    or y + h <= 0
                    or y >= self.canvas_h
                )
                partially_outside = (
                    x < -1
                    or y < -1
                    or x + w > self.canvas_w + 1
                    or y + h > self.canvas_h + 1
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
            self.log(page_ref, "WARNING", f'Missing layer field: element "{eid}"')

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
                    if (
                        key not in self.theme_text_styles
                        and key not in self.theme_table_styles
                    ):
                        self.log(
                            page_ref,
                            "ERROR",
                            f'element "{eid}" unknown style reference "{value}" at {field_path}',
                        )

    # -----------------------------------------------------------------------
    # New quality check methods
    # -----------------------------------------------------------------------

    def check_data_visualization_opportunity(
        self, page_ref: str, page_type: str, elements: list
    ):
        if page_type != "content":
            return

        has_viz = has_chart_table_timeline(elements)
        has_timeline = has_timeline_step_nodes(elements)

        for elem in elements:
            if elem.get("elementType") != "text":
                continue
            content = elem.get("content") or {}
            text = content.get("text", "")
            if not isinstance(text, str):
                continue

            bullet_count = count_bullet_items(text)
            if bullet_count >= 4 and not has_viz:
                self.log(
                    page_ref,
                    "WARNING",
                    f"Data opportunity: bullet list with {bullet_count} items could be visualized as chart/table/timeline",
                )

            step_count = count_numbered_steps(text)
            if step_count >= 4 and not has_timeline:
                self.log(
                    page_ref,
                    "WARNING",
                    f"Data opportunity: numbered steps with {step_count} items could be visualized as timeline",
                )

    def check_layout_quality(self, page_ref: str, elements: list):
        self.check_card_alignment(page_ref, elements)
        self.check_whitespace_distribution(page_ref, elements)
        self.check_typography_hierarchy(page_ref, elements)
        self.check_decoration_density(page_ref, elements)

    def check_card_alignment(self, page_ref: str, elements: list):
        cards = [e for e in elements if is_card(e)]
        if len(cards) < 2:
            return

        card_data = []
        for card in cards:
            x, y, w, h = [float(v) for v in card["bounds"]]
            card_data.append((x, y, w, h))

        # Group cards by row (y within 20px) and check per row
        from itertools import groupby
        sorted_by_y = sorted(card_data, key=lambda c: (c[1], c[0]))
        rows = []
        current_row = []
        current_y = None
        for c in sorted_by_y:
            if current_y is None or abs(c[1] - current_y) > 20:
                if current_row:
                    rows.append(current_row)
                current_row = [c]
                current_y = c[1]
            else:
                current_row.append(c)
        if current_row:
            rows.append(current_row)

        for row in rows:
            if len(row) < 2:
                continue
            # Check width consistency within row
            widths = [c[2] for c in row]
            min_w, max_w = min(widths), max(widths)
            if max_w - min_w > 10:
                self.log(
                    page_ref,
                    "WARNING",
                    f"Card alignment inconsistent: card widths vary by {int(max_w - min_w)}px",
                )
                continue
            # Check even horizontal spacing
            row_sorted = sorted(row, key=lambda c: c[0])
            gaps = []
            for i in range(1, len(row_sorted)):
                prev_right = row_sorted[i - 1][0] + row_sorted[i - 1][2]
                curr_left = row_sorted[i][0]
                gap = curr_left - prev_right
                gaps.append(gap)
            if gaps:
                min_gap, max_gap = min(gaps), max(gaps)
                if max_gap - min_gap > 10:
                    self.log(
                        page_ref,
                        "WARNING",
                        f"Card alignment inconsistent: horizontal gaps vary by {int(max_gap - min_gap)}px",
                    )

    def check_whitespace_distribution(self, page_ref: str, elements: list):
        content_elements = [
            e
            for e in elements
            if e.get("elementType") in ("text", "chart", "table", "image")
        ]
        if not content_elements:
            return

        min_x = min(float(e["bounds"][0]) for e in content_elements)
        min_y = min(float(e["bounds"][1]) for e in content_elements)
        max_x = max(
            float(e["bounds"][0]) + float(e["bounds"][2]) for e in content_elements
        )
        max_y = max(
            float(e["bounds"][1]) + float(e["bounds"][3]) for e in content_elements
        )

        bbox_height = max_y - min_y

        if bbox_height < 0.4 * self.canvas_h:
            self.log(
                page_ref,
                "WARNING",
                "Content may be too sparse; consider expanding or using a different layout",
            )

        if max_y < self.canvas_h / 2:
            self.log(
                page_ref,
                "WARNING",
                "Content concentrated in top half; consider vertical centering",
            )

    def check_typography_hierarchy(self, page_ref: str, elements: list):
        font_sizes = set()
        for elem in elements:
            if elem.get("elementType") != "text":
                continue
            content = elem.get("content") or {}
            if not isinstance(content, dict):
                continue

            font_size = None
            # Check styleRef at element level first (PPTD standard)
            style_ref = elem.get("styleRef") or content.get("style")
            if isinstance(style_ref, str) and style_ref.startswith("$"):
                key = style_ref[1:]
                resolved = self.theme_text_styles.get(key) or {}
                font_size = resolved.get("fontSize")
            elif isinstance(style_ref, dict):
                font_size = style_ref.get("fontSize")

            if font_size is None:
                font_size = elem.get("fontSize") or content.get("fontSize")
            if font_size is None:
                font_size = 18.0
            else:
                font_size = float(font_size)

            font_sizes.add(font_size)

        if len(font_sizes) < 2:
            self.log(
                page_ref,
                "WARNING",
                "Typography hierarchy weak; consider using display + body size contrast",
            )

    def is_decoration(self, elem: dict) -> bool:
        if elem.get("elementType") != "shape":
            return False
        # Exclude cards
        if is_card(elem):
            return False
        # Exclude timeline / step nodes (functional layout elements, not decorative)
        eid = elem.get("elementId", "")
        if eid.startswith("step-") or "timeline" in eid or "-dot" in eid or eid.startswith("node"):
            return False

        bounds = elem.get("bounds")
        if not isinstance(bounds, (list, tuple)) or len(bounds) != 4:
            return False
        x, y, w, h = [float(v) for v in bounds]

        opacity = elem.get("opacity")
        if opacity is None:
            opacity = 1.0
        else:
            opacity = float(opacity)

        # Small shape
        is_small = w < 150 or h < 100
        # Near edges
        near_edge = (
            x < 50
            or y < 50
            or x + w > self.canvas_w - 50
            or y + h > self.canvas_h - 50
        )
        # Low opacity
        low_opacity = opacity < 1.0

        return is_small or near_edge or low_opacity

    def check_decoration_density(self, page_ref: str, elements: list):
        decorations = [e for e in elements if self.is_decoration(e)]

        if len(decorations) > 5:
            self.log(
                page_ref,
                "WARNING",
                "Too many decorations; max recommended is 3 per slide",
            )

        is_minimal = self.is_minimal_style()
        if len(decorations) == 0 and not is_minimal:
            self.log(
                page_ref,
                "WARNING",
                "Missing decorations; most styles need 1-3 decorative elements",
            )

    def is_minimal_style(self) -> bool:
        path_parts = set(self.pptd_path.parts)
        return bool(path_parts & MINIMAL_STYLES)

    def _resolve_color(self, color_str: str) -> Optional[str]:
        """Resolve a color reference ($primary) to its hex value."""
        if not color_str or not isinstance(color_str, str):
            return None
        if color_str.startswith('$'):
            key = color_str[1:]
            return self.theme_colors.get(key, color_str)
        if color_str.startswith('#'):
            return color_str
        return None

    def check_chart_annotations(self, page_ref: str, elements: list):
        """Warn if charts lack titles, legends, or data labels."""
        for elem in elements:
            if elem.get('elementType') != 'chart':
                continue
            eid = elem.get('elementId', '<unknown>')
            title = elem.get('title')
            legend = elem.get('legend', True)
            data_labels = elem.get('dataLabels')
            has_annotation = bool(title) or (legend is not False) or (data_labels is not False)
            if not has_annotation:
                self.log(
                    page_ref,
                    "WARNING",
                    f"Chart '{eid}' lacks title, legend, or data labels — viewers won't understand the data",
                )

    def check_text_contrast(self, page_ref: str, elements: list):
        """Warn if text colors may have insufficient contrast against backgrounds."""
        # Determine effective background color for the page
        bg_color_str = None
        for elem in elements:
            if elem.get('elementType') == 'shape' and elem.get('bounds', [0, 0, 0, 0]) == [0, 0, self.canvas_w, self.canvas_h]:
                fill = elem.get('fill', {})
                if isinstance(fill, dict) and fill.get('type') == 'solid':
                    bg_color_str = fill.get('color')
                    break
        # Fallback to page background or theme background
        if not bg_color_str:
            for elem in elements:
                bg = elem.get('bgColor') or elem.get('background')
                if isinstance(bg, str):
                    bg_color_str = bg
                    break
        if not bg_color_str:
            bg_color_str = self.theme_colors.get('background', '#FFFFFF')
        
        bg_hex = self._resolve_color(bg_color_str)
        if not bg_hex or not bg_hex.startswith('#'):
            return
        
        try:
            bg_lum = _luminance(bg_hex)
        except (ValueError, IndexError):
            return
        
        for elem in elements:
            if elem.get('elementType') not in ('text', 'shape', 'table'):
                continue
            eid = elem.get('elementId', '<unknown>')
            
            # Determine effective background for this element
            # Default to slide background; if element is a shape with its own fill, use that
            current_bg_hex = bg_hex
            current_bg_lum = bg_lum
            if elem.get('elementType') == 'shape':
                fill = elem.get('fill', {})
                if isinstance(fill, dict) and fill.get('type') == 'solid':
                    resolved = self._resolve_color(fill.get('color'))
                    if resolved and resolved.startswith('#'):
                        try:
                            current_bg_hex = resolved
                            current_bg_lum = _luminance(current_bg_hex)
                        except (ValueError, IndexError):
                            pass
            
            # Check text color
            content = elem.get('content', {})
            if isinstance(content, dict):
                color_str = content.get('color')
                if color_str:
                    resolved = self._resolve_color(color_str)
                    if resolved and resolved.startswith('#'):
                        try:
                            text_lum = _luminance(resolved)
                            ratio = (max(text_lum, current_bg_lum) + 0.05) / (min(text_lum, current_bg_lum) + 0.05)
                            if ratio < 3.0:
                                self.log(
                                    page_ref,
                                    "WARNING",
                                    f"Element '{eid}' text color ({resolved}) may have poor contrast ({ratio:.1f}:1) against background ({current_bg_hex})",
                                )
                        except (ValueError, IndexError):
                            pass

    def check_card_consistency_across_pages(self):
        if not self.cards_across_pages:
            return
        widths = [bw for _, bw in self.cards_across_pages]
        distinct_widths = sorted(set(widths))
        if len(distinct_widths) > 1:
            self.log(
                "deck",
                "WARNING",
                f"Card border width inconsistent across pages: found widths {distinct_widths}",
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
