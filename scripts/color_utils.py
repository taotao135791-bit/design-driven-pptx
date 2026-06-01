#!/usr/bin/env python3
"""
Unified color utility library for design-driven-pptx.
Supports HSL color space operations, contrast calculations, and dynamic adaptation.
All functions operate on #RRGGBB hex strings.
"""

from typing import Tuple


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert #RRGGBB or #RRGGBBAA to (r, g, b) tuple."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) < 6:
        raise ValueError(f"Invalid hex color: #{hex_color}")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB values to #RRGGBB hex string."""
    return "#{:02x}{:02x}{:02x}".format(
        max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
    )


def hex_to_hsl(hex_color: str) -> Tuple[float, float, float]:
    """Convert hex color to HSL tuple (h: 0-360, s: 0-1, l: 0-1)."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) < 6:
        raise ValueError(f"Invalid hex color: #{hex_color}")
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


def hsl_to_hex(h: float, s: float, l: float) -> str:
    """Convert HSL values to #RRGGBB hex color string."""
    def _hue_to_rgb(p: float, q: float, t: float) -> float:
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
        r = _hue_to_rgb(p, q, h / 360 + 1/3)
        g = _hue_to_rgb(p, q, h / 360)
        b = _hue_to_rgb(p, q, h / 360 - 1/3)

    return "#{:02x}{:02x}{:02x}".format(
        max(0, min(255, int(round(r * 255)))),
        max(0, min(255, int(round(g * 255)))),
        max(0, min(255, int(round(b * 255)))),
    )


def adjust_saturation(hex_color: str, factor: float) -> str:
    """
    Adjust color saturation.
    factor < 1.0 reduces saturation, factor > 1.0 increases it.
    """
    h, s, l = hex_to_hsl(hex_color)
    s = max(0.0, min(1.0, s * factor))
    return hsl_to_hex(h, s, l)


def adjust_lightness(hex_color: str, factor: float) -> str:
    """
    Adjust color lightness in HSL space.
    factor < 1.0 darkens, factor > 1.0 lightens.
    Result is clamped to [0.0, 1.0].
    """
    h, s, l = hex_to_hsl(hex_color)
    new_l = max(0.0, min(1.0, l * factor))
    return hsl_to_hex(h, s, new_l)


def adjust_contrast(hex_color: str, factor: float) -> str:
    """
    Adjust color contrast by pushing lightness away from mid-gray (0.5).
    factor > 1.0 increases contrast, factor < 1.0 decreases it.
    """
    h, s, l = hex_to_hsl(hex_color)
    if l > 0.5:
        l = 0.5 + (l - 0.5) * factor
    else:
        l = 0.5 - (0.5 - l) * factor
    l = max(0.0, min(1.0, l))
    return hsl_to_hex(h, s, l)


def luminance(hex_color: str) -> float:
    """Calculate WCAG relative luminance of a color."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) < 6:
        raise ValueError(f"Invalid hex color: #{hex_color}")
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
    g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
    b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(hex1: str, hex2: str) -> float:
    """Calculate WCAG contrast ratio between two colors."""
    l1 = luminance(hex1)
    l2 = luminance(hex2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def ensure_contrast(
    hex_color: str, target_contrast: float = 4.5, against: str = "#FFFFFF"
) -> str:
    """
    Adjust a color (lighten or darken) until it achieves target contrast ratio.
    Uses binary search in HSL lightness space for precise results.
    """
    target_lum = luminance(against)
    color_lum = luminance(hex_color)

    h, s, l = hex_to_hsl(hex_color)

    if color_lum < target_lum:
        # Color is darker than background, need to darken further
        target_dark_lum = (target_lum + 0.05) / target_contrast - 0.05
        target_dark_lum = max(0.0, target_dark_lum)
        low, high = 0.0, l
        for _ in range(20):
            mid = (low + high) / 2
            test_hex = hsl_to_hex(h, s, mid)
            test_lum = luminance(test_hex)
            if test_lum > target_dark_lum:
                high = mid
            else:
                low = mid
        return hsl_to_hex(h, s, low)
    else:
        # Color is lighter than background, need to lighten further
        target_light_lum = target_contrast * (target_lum + 0.05) - 0.05
        target_light_lum = min(1.0, target_light_lum)
        low, high = l, 1.0
        for _ in range(20):
            mid = (low + high) / 2
            test_hex = hsl_to_hex(h, s, mid)
            test_lum = luminance(test_hex)
            if test_lum < target_light_lum:
                low = mid
            else:
                high = mid
        return hsl_to_hex(h, s, high)


def darken_for_contrast(
    hex_color: str, target_contrast: float = 4.5, against: str = "#FFFFFF"
) -> str:
    """Darken a color until it achieves target contrast ratio."""
    return ensure_contrast(hex_color, target_contrast, against)


def adapt_color(hex_color: str, tone: str = "serious") -> str:
    """
    Apply complete tone adaptation to a color.
    tone: serious | creative | data_intensive | educational | promotional
    """
    rules = {
        "serious": {"saturation": 0.7, "lightness": 1.0, "contrast": 1.0},
        "creative": {"saturation": 1.2, "lightness": 1.0, "contrast": 1.15},
        "data_intensive": {"saturation": 0.85, "lightness": 1.05, "contrast": 1.1},
        "educational": {"saturation": 0.9, "lightness": 1.02, "contrast": 1.05},
        "promotional": {"saturation": 1.15, "lightness": 1.0, "contrast": 1.1},
    }
    rule = rules.get(tone, rules["serious"])
    h, s, l = hex_to_hsl(hex_color)
    s = max(0.0, min(1.0, s * rule["saturation"]))
    l = max(0.0, min(1.0, l * rule["lightness"]))
    if l > 0.5:
        l = 0.5 + (l - 0.5) * rule["contrast"]
    else:
        l = 0.5 - (0.5 - l) * rule["contrast"]
    l = max(0.0, min(1.0, l))
    return hsl_to_hex(h, s, l)


def classify_palette(colors_data: list) -> dict:
    """
    Classify extracted colors into design roles.
    colors_data: list of dicts with 'hex', 'rgb', 'count', 'ratio' keys.
    Returns a dict with primary, primaryDark, primaryText, background, surface,
    surfaceAlt, ink, text, textLight, white keys.
    """
    # Calculate HSL and luminance for each color
    for c in colors_data:
        c["hsl"] = hex_to_hsl(c["hex"])
        c["lum"] = luminance(c["hex"])

    # Sort by luminance
    by_lum = sorted(colors_data, key=lambda c: c["lum"])

    # Most frequent color
    most_frequent = colors_data[0]
    mf_lum = most_frequent["lum"]

    if mf_lum > 0.75:
        background = most_frequent["hex"]
        ink_candidates = [c for c in by_lum if c["lum"] < 0.25]
        ink = ink_candidates[0]["hex"] if ink_candidates else by_lum[0]["hex"]
    elif mf_lum < 0.2:
        background = most_frequent["hex"]
        ink_candidates = [c for c in by_lum if c["lum"] > 0.8]
        ink = ink_candidates[-1]["hex"] if ink_candidates else by_lum[-1]["hex"]
    else:
        background = most_frequent["hex"]
        ink = by_lum[0]["hex"] if by_lum[0]["lum"] < 0.3 else "#1A1A1A"

    # Primary/Accent: highest saturation, not too close to background or ink
    by_sat = sorted(colors_data, key=lambda c: c["hsl"][1], reverse=True)
    accent = None
    for c in by_sat:
        if c["hex"] != background and c["hex"] != ink and c["hsl"][1] > 0.15:
            accent = c["hex"]
            break
    if not accent:
        accent = by_sat[0]["hex"] if by_sat[0]["hex"] != background else "#E85D5D"

    primary = accent
    primary_dark = adjust_lightness(primary, 0.85)

    # Ensure primary-on-white contrast
    primary_lum = luminance(primary)
    white_on_primary = (1.0 + 0.05) / (primary_lum + 0.05)
    if white_on_primary < 4.5:
        primary_text = darken_for_contrast(primary, target_contrast=4.5, against="#FFFFFF")
    else:
        primary_text = primary

    # Text colors based on background luminance
    bg_lum = luminance(background)
    if bg_lum > 0.5:
        text = "#6B6B6B"
        text_light = "#B0B0B0"
        white = "#FFFFFF"
    else:
        text = "#A0A0A0"
        text_light = "#707070"
        white = "#FFFFFF"

    text_light = ensure_contrast(text_light, target_contrast=4.5, against=background)

    # Surface variants
    bg_hsl = hex_to_hsl(background)
    if bg_hsl[2] > 0.5:
        surface_alt = adjust_lightness(background, 0.92)
        surface = adjust_lightness(background, 0.96)
    else:
        surface_alt = adjust_lightness(background, 1.15)
        surface = adjust_lightness(background, 1.08)

    return {
        "primary": primary,
        "primaryDark": primary_dark,
        "primaryText": primary_text,
        "background": background,
        "surface": surface,
        "surfaceAlt": surface_alt,
        "ink": ink,
        "text": text,
        "textLight": text_light,
        "white": white,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python color_utils.py <hex_color> <tone>")
        print("  tone: serious | creative | data_intensive | educational | promotional")
        sys.exit(1)
    color = sys.argv[1]
    tone = sys.argv[2]
    adapted = adapt_color(color, tone)
    print(f"Original: {color}")
    print(f"Adapted ({tone}): {adapted}")
