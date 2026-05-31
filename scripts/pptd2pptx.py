#!/usr/bin/env python3
"""
PPTD to PPTX Converter
Converts .pptd presentations (YAML-based intermediate format) to .pptx files.
Requires: python-pptx, PyYAML
Optional: resvg (for SVG decoration support)

Usage:
    python pptd2pptx.py <path-to.pptd> [<output.pptx>]
"""

import sys
import os
import re
import copy
import tempfile
from html.parser import HTMLParser

import yaml
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.chart import XL_CHART_TYPE
from pptx.oxml.ns import nsmap, qn
from pptx.oxml import parse_xml

# Optional resvg for SVG rendering
try:
    import resvg
    RESVG_AVAILABLE = True
except ImportError:
    RESVG_AVAILABLE = False

# ---------------------------------------------------------------------------
# Coordinate mapping
# ---------------------------------------------------------------------------
PPTD_WIDTH = 1280.0
PPTD_HEIGHT = 720.0


def px_to_emu(val, slide_dim_emu, total_px):
    """Map PPTD px to EMU proportionally."""
    return int(val / total_px * slide_dim_emu)


# ---------------------------------------------------------------------------
# Color / Theme helpers
# ---------------------------------------------------------------------------
def hex_to_rgb(hex_color):
    """Convert #RRGGBB or #RRGGBBAA to RGBColor (ignores alpha)."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) >= 6:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return RGBColor(r, g, b)
    return RGBColor(0, 0, 0)


# ---------------------------------------------------------------------------
# Color manipulation utilities (for dynamic color adaptation)
# ---------------------------------------------------------------------------
def hex_to_hsl(hex_color):
    """Convert hex to HSL tuple (h, s, l) where h in [0,360], s,l in [0,1]."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    l = (mx + mn) / 2.0
    if mx == mn:
        h = s = 0.0
    else:
        d = mx - mn
        s = d / (2.0 - mx - mn) if l > 0.5 else d / (mx + mn)
        if mx == r:
            h = (60 * ((g - b) / d) + 360) % 360
        elif mx == g:
            h = (60 * ((b - r) / d) + 120) % 360
        else:
            h = (60 * ((r - g) / d) + 240) % 360
    return (h, s, l)


def hsl_to_hex(h, s, l):
    """Convert HSL to hex color string."""
    def hue_to_rgb(p, q, t):
        if t < 0:
            t += 1
        if t > 1:
            t -= 1
        if t < 1/6:
            return p + (q - p) * 6 * t
        if t < 1/2:
            return q
        if t < 2/3:
            return p + (q - p) * (2/3 - t) * 6
        return p

    if s == 0:
        r = g = b = l
    else:
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h / 360 + 1/3)
        g = hue_to_rgb(p, q, h / 360)
        b = hue_to_rgb(p, q, h / 360 - 1/3)

    return "#{:02x}{:02x}{:02x}".format(
        int(round(r * 255)), int(round(g * 255)), int(round(b * 255))
    )


def adjust_saturation(hex_color, factor):
    """Adjust color saturation by factor (0.0-1.0 reduces, >1.0 increases)."""
    h, s, l = hex_to_hsl(hex_color)
    s = max(0.0, min(1.0, s * factor))
    return hsl_to_hex(h, s, l)


def adjust_lightness(hex_color, factor):
    """Adjust color lightness by factor (0.0-1.0 darkens, >1.0 lightens)."""
    h, s, l = hex_to_hsl(hex_color)
    l = max(0.0, min(1.0, l * factor))
    return hsl_to_hex(h, s, l)


def adjust_contrast(hex_color, factor):
    """Adjust color contrast: factor > 1 pushes away from mid-gray, < 1 pulls toward."""
    h, s, l = hex_to_hsl(hex_color)
    if l > 0.5:
        l = 0.5 + (l - 0.5) * factor
    else:
        l = 0.5 - (0.5 - l) * factor
    l = max(0.0, min(1.0, l))
    return hsl_to_hex(h, s, l)


class ThemeResolver:
    def __init__(self, theme_yaml):
        self.colors = theme_yaml.get('colors', {})
        self.text_styles = theme_yaml.get('textStyles', {})
        self.table_styles = theme_yaml.get('tableStyles', {})

    def resolve_color(self, color_str):
        if not color_str:
            return None
        if color_str.startswith('$'):
            key = color_str[1:]
            color_str = self.colors.get(key, color_str)
        if color_str.startswith('#'):
            return hex_to_rgb(color_str)
        return None

    def resolve_text_style(self, style_ref):
        if not style_ref:
            return {}
        if style_ref.startswith('$'):
            key = style_ref[1:]
            return copy.deepcopy(self.text_styles.get(key, {}))
        return {}


# ---------------------------------------------------------------------------
# SVG helper
# ---------------------------------------------------------------------------
def svg_to_png_bytes(svg_path):
    """Render SVG file to PNG bytes using resvg. Returns None if unavailable."""
    if not RESVG_AVAILABLE:
        return None
    try:
        with open(svg_path, 'rb') as f:
            svg_data = f.read()
        opts = resvg.usvg.Options.default()
        tree = resvg.usvg.Tree.from_str(svg_data.decode('utf-8'), opts)
        # Get size for proper rendering
        size = tree.int_size()
        # Render at 2x for better quality
        transform = (2.0, 0.0, 0.0, 2.0, 0.0, 0.0)
        png = resvg.render(tree, transform)
        return png
    except Exception as e:
        print(f"Warning: SVG rendering failed for {svg_path}: {e}")
        return None


# ---------------------------------------------------------------------------
# HTML Rich Text Parser
# ---------------------------------------------------------------------------
class RichTextState:
    def __init__(self):
        self.bold = False
        self.italic = False
        self.underline = False
        self.strike = False
        self.sup = False
        self.sub = False
        self.color = None
        self.font_size = None
        self.font_family = None
        self.href = None


class RichTextSegment:
    def __init__(self, text, state, para_style=None):
        self.text = text
        self.state = state
        self.para_style = para_style or {}


class RichTextParser(HTMLParser):
    """Parse PPTD rich text (subset of HTML) into segments."""

    def __init__(self):
        super().__init__()
        self.segments = []
        self.state_stack = [RichTextState()]
        self.para_style = {}
        self.current_text = []

    def _current_state(self):
        base = RichTextState()
        for st in self.state_stack:
            base.bold = base.bold or st.bold
            base.italic = base.italic or st.italic
            base.underline = base.underline or st.underline
            base.strike = base.strike or st.strike
            base.sup = base.sup or st.sup
            base.sub = base.sub or st.sub
            if st.color:
                base.color = st.color
            if st.font_size:
                base.font_size = st.font_size
            if st.font_family:
                base.font_family = st.font_family
            if st.href:
                base.href = st.href
        return base

    def _flush(self):
        if self.current_text:
            text = ''.join(self.current_text)
            if text:
                self.segments.append(RichTextSegment(
                    text, self._current_state(), dict(self.para_style)
                ))
            self.current_text = []

    def handle_starttag(self, tag, attrs):
        self._flush()
        attrs_dict = dict(attrs)
        if tag == 'p':
            self.para_style = {}
            style = attrs_dict.get('style', '')
            if 'text-align:' in style:
                m = re.search(r'text-align:\s*(left|center|right|justify)', style)
                if m:
                    self.para_style['align'] = m.group(1)
            if 'line-height:' in style:
                m = re.search(r'line-height:\s*([0-9.]+)', style)
                if m:
                    self.para_style['line_height'] = float(m.group(1))
            if 'margin-top:' in style:
                m = re.search(r'margin-top:\s*([0-9]+)px', style)
                if m:
                    self.para_style['space_before'] = int(m.group(1))
        elif tag == 'span':
            st = RichTextState()
            style = attrs_dict.get('style', '')
            if 'color:' in style:
                m = re.search(r'color:\s*([^;\s]+)', style)
                if m:
                    st.color = m.group(1)
            if 'font-size:' in style:
                m = re.search(r'font-size:\s*([0-9]+)px', style)
                if m:
                    st.font_size = int(m.group(1))
            if 'font-family:' in style:
                m = re.search(r"font-family:([^;]+)", style)
                if m:
                    st.font_family = m.group(1).strip().strip('"')
            self.state_stack.append(st)
        elif tag == 'strong':
            st = RichTextState(); st.bold = True
            self.state_stack.append(st)
        elif tag == 'em':
            st = RichTextState(); st.italic = True
            self.state_stack.append(st)
        elif tag == 'u':
            st = RichTextState(); st.underline = True
            self.state_stack.append(st)
        elif tag == 's':
            st = RichTextState(); st.strike = True
            self.state_stack.append(st)
        elif tag == 'sup':
            st = RichTextState(); st.sup = True
            self.state_stack.append(st)
        elif tag == 'sub':
            st = RichTextState(); st.sub = True
            self.state_stack.append(st)
        elif tag == 'a':
            st = RichTextState()
            st.href = attrs_dict.get('href', '')
            self.state_stack.append(st)
        elif tag in ('ul', 'ol'):
            self.para_style['bullet'] = True
            self.para_style['bullet_type'] = 'bullet' if tag == 'ul' else 'number'
        elif tag == 'br':
            self.current_text.append('\n')

    def handle_endtag(self, tag):
        self._flush()
        if tag in ('p', 'span', 'strong', 'em', 'u', 's', 'sup', 'sub', 'a'):
            if len(self.state_stack) > 1:
                self.state_stack.pop()
        elif tag in ('ul', 'ol'):
            self.para_style['bullet'] = False

    def handle_data(self, data):
        self.current_text.append(data)

    def get_segments(self):
        self._flush()
        return self.segments


def parse_rich_text(html_text):
    """Parse rich text string into list of RichTextSegment."""
    if '<' not in html_text:
        html_text = f'<p>{html_text}</p>'
    parser = RichTextParser()
    parser.feed(html_text)
    return parser.get_segments()


# ---------------------------------------------------------------------------
# Alignment mapping
# ---------------------------------------------------------------------------
H_ALIGN_MAP = {
    'left': PP_ALIGN.LEFT,
    'center': PP_ALIGN.CENTER,
    'right': PP_ALIGN.RIGHT,
    'justify': PP_ALIGN.JUSTIFY,
    'distributed': PP_ALIGN.DISTRIBUTE,
}

V_ALIGN_MAP = {
    'top': MSO_ANCHOR.TOP,
    'middle': MSO_ANCHOR.MIDDLE,
    'bottom': MSO_ANCHOR.BOTTOM,
}


# ---------------------------------------------------------------------------
# Shape name mapping
# ---------------------------------------------------------------------------
SHAPE_MAP = {
    'rect': MSO_SHAPE.RECTANGLE,
    'roundRect': MSO_SHAPE.ROUNDED_RECTANGLE,
    'ellipse': MSO_SHAPE.OVAL,
    'triangle': MSO_SHAPE.ISOSCELES_TRIANGLE,
    'diamond': MSO_SHAPE.DIAMOND,
    'plus': MSO_SHAPE.CROSS,
    'star5': MSO_SHAPE.STAR_5_POINT,
    'rightArrow': MSO_SHAPE.RIGHT_ARROW,
    'homePlate': MSO_SHAPE.PENTAGON,
    'chevron': MSO_SHAPE.CHEVRON,
    'donut': MSO_SHAPE.DONUT,
    'flowChartProcess': MSO_SHAPE.FLOWCHART_PROCESS,
    'flowChartDecision': MSO_SHAPE.FLOWCHART_DECISION,
    'flowChartTerminator': MSO_SHAPE.FLOWCHART_TERMINATOR,
}


# ---------------------------------------------------------------------------
# Chart type mapping (PPTD -> python-pptx)
# ---------------------------------------------------------------------------
CHART_TYPE_MAP = {
    'bar': {'vertical': 'COLUMN_CLUSTERED', 'horizontal': 'BAR_CLUSTERED'},
    'line': 'LINE_MARKERS',
    'area': 'AREA',
    'scatter': 'XY_SCATTER',
    'pie': 'PIE',
    'radar': 'RADAR',
    'combo': 'COLUMN_CLUSTERED',  # fallback, handled separately
    'bubble': 'BUBBLE',
}


# ---------------------------------------------------------------------------
# Converter
# ---------------------------------------------------------------------------
class PPTDConverter:
    def __init__(self, pptd_path):
        self.pptd_path = pptd_path
        self.base_dir = os.path.dirname(os.path.abspath(pptd_path))
        with open(pptd_path, encoding='utf-8') as f:
            self.pptd = yaml.safe_load(f)
        self.theme = ThemeResolver(self.pptd.get('theme', {}))
        size = self.pptd.get('size', [1280, 720])
        self.pptd_w, self.pptd_h = size[0], size[1]
        self.prs = Presentation()
        # Set slide dimensions: 16:9 widescreen ~ 13.333 x 7.5 inches
        self.slide_width_emu = 12192000  # 13.333 inches
        self.slide_height_emu = 6858000  # 7.5 inches
        self.prs.slide_width = Emu(self.slide_width_emu)
        self.prs.slide_height = Emu(self.slide_height_emu)

    def _to_emu(self, x, y, w, h):
        """Convert PPTD bounds [x,y,w,h] to EMU."""
        x_emu = px_to_emu(x, self.slide_width_emu, self.pptd_w)
        y_emu = px_to_emu(y, self.slide_height_emu, self.pptd_h)
        w_emu = px_to_emu(w, self.slide_width_emu, self.pptd_w)
        h_emu = px_to_emu(h, self.slide_height_emu, self.pptd_h)
        return x_emu, y_emu, w_emu, h_emu

    def _resolve_style(self, content):
        """Merge text style: theme style + inline overrides."""
        style = {}
        style_ref = content.get('style')
        if style_ref:
            style = self.theme.resolve_text_style(style_ref)
        for key in ('fontSize', 'color', 'fontFamily', 'lineHeight',
                    'lineHeightPx', 'letterSpacing', 'marginTop'):
            if key in content:
                style[key] = content[key]
        return style

    def _apply_fill(self, shape, fill_spec):
        if not fill_spec:
            return
        fill_type = fill_spec.get('type')
        if fill_type == 'solid':
            color = self.theme.resolve_color(fill_spec.get('color'))
            if color:
                shape.fill.solid()
                shape.fill.fore_color.rgb = color
        elif fill_type == 'gradient':
            grad_type = fill_spec.get('gradientType', 'linear')
            stops = fill_spec.get('stops', [])
            if stops and len(stops) >= 2:
                shape.fill.gradient()
                color = self.theme.resolve_color(stops[0].get('color'))
                if color:
                    shape.fill.fore_color.rgb = color
        elif fill_type == 'image':
            src = fill_spec.get('src', '')
            if src and os.path.exists(src):
                shape.fill.background()

    def _apply_border(self, shape, border_spec):
        if not border_spec:
            return
        width = border_spec.get('width', 1)
        color = self.theme.resolve_color(border_spec.get('color'))
        if color:
            shape.line.color.rgb = color
            shape.line.width = Pt(width)
        else:
            shape.line.fill.background()

    def _apply_shadow(self, shape, shadow_spec):
        pass

    def _add_text_frame(self, shape, content):
        """Add rich text to a shape's text frame."""
        tf = shape.text_frame
        tf.word_wrap = content.get('wrap', True)
        tf.auto_size = None

        align = content.get('align', ['left', 'top'])
        h_align = H_ALIGN_MAP.get(align[0], PP_ALIGN.LEFT)
        v_align = V_ALIGN_MAP.get(align[1], MSO_ANCHOR.TOP)
        tf.paragraphs[0].alignment = h_align

        base_style = self._resolve_style(content)
        html_text = content.get('text', '')
        segments = parse_rich_text(html_text)

        if not segments:
            return

        current_para = tf.paragraphs[0]
        first = True

        for seg in segments:
            if '\n' in seg.text and not first:
                parts = seg.text.split('\n')
                for i, part in enumerate(parts):
                    if i > 0:
                        current_para = tf.add_paragraph()
                        current_para.alignment = h_align
                    if part:
                        run = current_para.add_run()
                        run.text = part
                        self._apply_run_style(run, seg.state, base_style)
            else:
                run = current_para.add_run()
                run.text = seg.text
                self._apply_run_style(run, seg.state, base_style)

            if seg.para_style.get('space_before'):
                current_para.space_before = Pt(seg.para_style['space_before'])
            if seg.para_style.get('line_height'):
                current_para.line_spacing = seg.para_style['line_height']

            first = False

        if len(tf.paragraphs) > 1 and not tf.paragraphs[0].text:
            p = tf.paragraphs[0]
            p._element.getparent().remove(p._element)

    def _apply_run_style(self, run, state, base_style):
        """Apply font styling to a run."""
        font = run.font
        font.bold = state.bold or base_style.get('fontBold', False)
        font.italic = state.italic or base_style.get('fontItalic', False)
        if state.underline or base_style.get('fontUnderline', False):
            font.underline = True

        color_str = state.color or base_style.get('color')
        color = self.theme.resolve_color(color_str)
        if color:
            font.color.rgb = color

        size = state.font_size or base_style.get('fontSize')
        if size:
            font.size = Pt(size)

        family = state.font_family or base_style.get('fontFamily')
        if family:
            font.name = family.split(',')[0].strip()

        if state.sup:
            font._element.set(qn('a:baseline'), '30000')
        elif state.sub:
            font._element.set(qn('a:baseline'), '-30000')

    def _add_shape(self, slide, element):
        bounds = element.get('bounds', [0, 0, 100, 100])
        x, y, w, h = self._to_emu(*bounds)
        shape_name = element.get('shapeName', 'rect')
        rotation = element.get('rotation', 0)

        mso_shape = SHAPE_MAP.get(shape_name, MSO_SHAPE.RECTANGLE)

        shape = slide.shapes.add_shape(mso_shape, Emu(x), Emu(y), Emu(w), Emu(h))
        shape.rotation = rotation

        fill_spec = element.get('fill')
        if fill_spec:
            self._apply_fill(shape, fill_spec)
        else:
            shape.fill.background()

        border_spec = element.get('border')
        self._apply_border(shape, border_spec)

        shadow_spec = element.get('shadow')
        if shadow_spec:
            self._apply_shadow(shape, shadow_spec)

        opacity = element.get('opacity', 1)
        if opacity < 1:
            pass

        return shape

    def _add_text(self, slide, element):
        bounds = element.get('bounds', [0, 0, 100, 100])
        x, y, w, h = self._to_emu(*bounds)

        shape = slide.shapes.add_textbox(Emu(x), Emu(y), Emu(w), Emu(h))
        content = element.get('content', {})
        self._add_text_frame(shape, content)
        return shape

    def _add_image(self, slide, element):
        bounds = element.get('bounds', [0, 0, 100, 100])
        x, y, w, h = self._to_emu(*bounds)
        src = element.get('src', '')

        if not src:
            return None

        if not os.path.isabs(src):
            src = os.path.join(self.base_dir, src)

        if not os.path.exists(src):
            print(f"Warning: image not found: {src}")
            return None

        # Handle SVG images using resvg
        if src.lower().endswith('.svg'):
            png_bytes = svg_to_png_bytes(src)
            if png_bytes:
                # Write to temp file for add_picture
                fd, tmp_path = tempfile.mkstemp(suffix='.png')
                try:
                    with os.fdopen(fd, 'wb') as f:
                        f.write(png_bytes)
                    shape = slide.shapes.add_picture(tmp_path, Emu(x), Emu(y), Emu(w), Emu(h))
                finally:
                    try:
                        os.remove(tmp_path)
                    except OSError:
                        pass
            else:
                print(f"Warning: cannot render SVG {src} (install resvg: pip install resvg)")
                # Fallback: placeholder shape
                shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(x), Emu(y), Emu(w), Emu(h))
                shape.fill.solid()
                shape.fill.fore_color.rgb = RGBColor(240, 240, 240)
                tf = shape.text_frame
                p = tf.paragraphs[0]
                p.alignment = PP_ALIGN.CENTER
                run = p.add_run()
                run.text = "[SVG]"
                run.font.size = Pt(10)
                run.font.color.rgb = RGBColor(128, 128, 128)
                return shape
        else:
            shape = slide.shapes.add_picture(src, Emu(x), Emu(y), Emu(w), Emu(h))

        border_spec = element.get('border')
        self._apply_border(shape, border_spec)

        return shape

    def _add_table(self, slide, element):
        bounds = element.get('bounds', [0, 0, 100, 100])
        x, y, w, h = self._to_emu(*bounds)
        rows_data = element.get('rows', [])
        if not rows_data:
            return None

        num_rows = len(rows_data)
        num_cols = len(rows_data[0]) if rows_data else 0

        shape = slide.shapes.add_table(num_rows, num_cols, Emu(x), Emu(y), Emu(w), Emu(h))
        table = shape.table

        style_ref = element.get('style', '')
        table_style = {}
        if isinstance(style_ref, str) and style_ref.startswith('$'):
            table_style = self.theme.table_styles.get(style_ref[1:], {})
        elif isinstance(style_ref, dict):
            table_style = style_ref

        for r_idx, row_data in enumerate(rows_data):
            for c_idx, cell_data in enumerate(row_data):
                if c_idx >= num_cols:
                    break
                cell = table.cell(r_idx, c_idx)

                if r_idx == 0:
                    fill_color = table_style.get('headerFill')
                    text_color = table_style.get('headerColor')
                    is_bold = table_style.get('headerBold', True)
                else:
                    body_fill = table_style.get('bodyFill', [])
                    fill_color = body_fill[r_idx % len(body_fill)] if body_fill else None
                    text_color = table_style.get('bodyColor')
                    is_bold = False

                if fill_color:
                    color = self.theme.resolve_color(fill_color)
                    if color:
                        cell.fill.solid()
                        cell.fill.fore_color.rgb = color

                content = cell_data.get('content', {}) if isinstance(cell_data, dict) else {'text': str(cell_data)}
                if content:
                    self._add_text_frame(cell, content)
                    font_size = table_style.get('fontSize')
                    font_family = table_style.get('fontFamily')
                    for para in cell.text_frame.paragraphs:
                        if is_bold:
                            for run in para.runs:
                                run.font.bold = True
                        if text_color:
                            color = self.theme.resolve_color(text_color)
                            if color:
                                for run in para.runs:
                                    run.font.color.rgb = color
                        if font_size:
                            for run in para.runs:
                                run.font.size = Pt(font_size)
                        if font_family:
                            for run in para.runs:
                                run.font.name = font_family.split(',')[0].strip()

        return shape

    def _add_chart(self, slide, element):
        """Render a real chart using python-pptx chart API."""
        bounds = element.get('bounds', [0, 0, 100, 100])
        x, y, w, h = self._to_emu(*bounds)
        chart_type = element.get('type', 'bar')
        data = element.get('data', [])
        x_field = element.get('x', '')
        y_fields = element.get('y', [])
        names = element.get('names', [])
        colors = element.get('colors', [])
        options = element.get('options', {})

        if not data or not x_field or not y_fields:
            # Fallback to placeholder
            shape = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, Emu(x), Emu(y), Emu(w), Emu(h)
            )
            shape.fill.solid()
            shape.fill.fore_color.rgb = RGBColor(240, 240, 240)
            tf = shape.text_frame
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            run = p.add_run()
            run.text = f"[Chart: {chart_type}]"
            run.font.size = Pt(14)
            run.font.color.rgb = RGBColor(128, 128, 128)
            return shape

        # Normalize y_fields to list
        if isinstance(y_fields, str):
            y_fields = [y_fields]

        # Determine chart type enum
        direction = options.get('direction', 'vertical') if isinstance(options, dict) else 'vertical'
        if chart_type == 'bar':
            type_key = CHART_TYPE_MAP['bar'].get(direction, 'COLUMN_CLUSTERED')
        else:
            type_key = CHART_TYPE_MAP.get(chart_type, 'COLUMN_CLUSTERED')
        xl_type = getattr(XL_CHART_TYPE, type_key, XL_CHART_TYPE.COLUMN_CLUSTERED)

        # Build chart data
        from pptx.chart.data import ChartData, XyChartData, BubbleChartData

        if chart_type == 'scatter':
            chart_data = XyChartData()
            for idx, series_name in enumerate(y_fields):
                s = chart_data.add_series(names[idx] if idx < len(names) else series_name)
                for row in data:
                    x_val = row.get(x_field, 0)
                    y_val = row.get(series_name, 0)
                    s.add_data_point(x_val, y_val)
        elif chart_type == 'bubble':
            chart_data = BubbleChartData()
            size_field = element.get('size', '')
            for idx, series_name in enumerate(y_fields):
                s = chart_data.add_series(names[idx] if idx < len(names) else series_name)
                for row in data:
                    x_val = row.get(x_field, 0)
                    y_val = row.get(series_name, 0)
                    size_val = row.get(size_field, 10) if size_field else 10
                    s.add_data_point(x_val, y_val, size_val)
        else:
            chart_data = ChartData()
            categories = [str(row.get(x_field, '')) for row in data]
            chart_data.categories = categories
            for idx, series_name in enumerate(y_fields):
                display_name = names[idx] if idx < len(names) else series_name
                values = [row.get(series_name, 0) for row in data]
                chart_data.add_series(display_name, values)

        # Add chart to slide
        try:
            graphic_frame = slide.shapes.add_chart(
                xl_type, Emu(x), Emu(y), Emu(w), Emu(h), chart_data
            )
            chart = graphic_frame.chart

            # Apply series colors
            if colors and hasattr(chart, 'series'):
                for idx, series in enumerate(chart.series):
                    if idx < len(colors):
                        color = self.theme.resolve_color(colors[idx])
                        if color:
                            series.format.fill.solid()
                            series.format.fill.fore_color.rgb = color

            # Apply chart title
            title = element.get('title', '')
            if title:
                if isinstance(title, str):
                    chart.has_title = True
                    chart.chart_title.text_frame.text = title
                elif isinstance(title, dict):
                    chart.has_title = True
                    chart.chart_title.text_frame.text = title.get('text', '')

            # Configure legend
            legend = element.get('legend', True)
            if legend is False:
                chart.has_legend = False
            elif isinstance(legend, dict):
                chart.has_legend = legend.get('show', True)
                if chart.has_legend and legend.get('position'):
                    from pptx.enum.chart import XL_LEGEND_POSITION
                    pos_map = {'top': XL_LEGEND_POSITION.TOP,
                               'bottom': XL_LEGEND_POSITION.BOTTOM,
                               'left': XL_LEGEND_POSITION.LEFT,
                               'right': XL_LEGEND_POSITION.RIGHT}
                    chart.legend.position = pos_map.get(legend['position'], XL_LEGEND_POSITION.BOTTOM)

            # Configure data labels
            data_labels = element.get('dataLabels')
            if data_labels and isinstance(data_labels, dict):
                if data_labels.get('show'):
                    for series in chart.series:
                        series.has_data_labels = True
                        if data_labels.get('content') == 'percentage':
                            from pptx.enum.chart import XL_LABEL_POSITION
                            # Note: percentage labels require specific handling per chart type

            # Configure donut inner radius
            if chart_type == 'pie' and isinstance(options, dict):
                inner_radius = options.get('innerRadius')
                if inner_radius and hasattr(chart, 'plot_type'):
                    # For doughnut charts, use DOUGHNUT type
                    pass

            return graphic_frame
        except Exception as e:
            print(f"Error rendering chart: {e}")
            # Fallback placeholder
            shape = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, Emu(x), Emu(y), Emu(w), Emu(h)
            )
            shape.fill.solid()
            shape.fill.fore_color.rgb = RGBColor(240, 240, 240)
            tf = shape.text_frame
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            run = p.add_run()
            run.text = f"[Chart: {chart_type}]"
            run.font.size = Pt(14)
            run.font.color.rgb = RGBColor(128, 128, 128)
            return shape

    def _add_icon(self, slide, element):
        bounds = element.get('bounds', [0, 0, 100, 100])
        x, y, w, h = self._to_emu(*bounds)
        icon_name = element.get('iconName', 'fas:question')

        shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Emu(x), Emu(y), Emu(w), Emu(h)
        )
        fill_spec = element.get('fill')
        if fill_spec:
            self._apply_fill(shape, fill_spec)

        tf = shape.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()
        run.text = f"[{icon_name}]"
        run.font.size = Pt(12)

        return shape

    def _set_background(self, slide, bg_spec):
        if not bg_spec:
            return
        bg_type = bg_spec.get('type')
        if bg_type == 'solid':
            color = self.theme.resolve_color(bg_spec.get('color'))
            if color:
                background = slide.background
                fill = background.fill
                fill.solid()
                fill.fore_color.rgb = color
        elif bg_type == 'gradient':
            stops = bg_spec.get('stops', [])
            if stops:
                background = slide.background
                fill = background.fill
                fill.gradient()
                color = self.theme.resolve_color(stops[0].get('color'))
                if color:
                    fill.fore_color.rgb = color
        elif bg_type == 'image':
            src = bg_spec.get('src', '')
            if src and os.path.exists(src):
                background = slide.background
                fill = background.fill
                fill.patterned()

    def convert_page(self, slide, page_data):
        """Convert a single .page data dict to a slide."""
        bg = page_data.get('background')
        if bg:
            self._set_background(slide, bg)

        for element in page_data.get('elements', []):
            etype = element.get('elementType')
            try:
                if etype == 'shape':
                    self._add_shape(slide, element)
                elif etype == 'text':
                    self._add_text(slide, element)
                elif etype == 'image':
                    self._add_image(slide, element)
                elif etype == 'table':
                    self._add_table(slide, element)
                elif etype == 'chart':
                    self._add_chart(slide, element)
                elif etype == 'icon':
                    self._add_icon(slide, element)
            except Exception as e:
                eid = element.get('elementId', 'unknown')
                print(f"Error processing element {eid} ({etype}): {e}")

    def convert(self, output_path=None):
        if output_path is None:
            base, _ = os.path.splitext(self.pptd_path)
            output_path = base + '.pptx'

        pages = self.pptd.get('pages', [])
        blank_layout = self.prs.slide_layouts[6]

        for page_ref in pages:
            page_path = os.path.join(self.base_dir, page_ref)
            if not os.path.exists(page_path):
                print(f"Warning: page file not found: {page_path}")
                continue

            with open(page_path, encoding='utf-8') as f:
                page_data = yaml.safe_load(f)

            slide = self.prs.slides.add_slide(blank_layout)
            self.convert_page(slide, page_data)

        self.prs.save(output_path)
        print(f"Saved: {output_path}")
        return output_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python pptd2pptx.py <path-to.pptd> [<output.pptx>]")
        sys.exit(1)

    pptd_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(pptd_path):
        print(f"File not found: {pptd_path}")
        sys.exit(1)

    converter = PPTDConverter(pptd_path)
    converter.convert(output_path)


if __name__ == '__main__':
    main()
