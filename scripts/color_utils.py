#!/usr/bin/env python3
"""
Color utility functions for dynamic color adaptation.
Supports HSL color space operations: saturation, lightness, contrast adjustments.
"""


def hex_to_hsl(hex_color):
    """Convert hex color to HSL tuple (h: 0-360, s: 0-1, l: 0-1)."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) < 6:
        raise ValueError(f"Invalid hex color: {hex_color}")
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
    """Convert HSL values to hex color string."""
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
    """
    Adjust color saturation.
    factor < 1.0 reduces saturation, factor > 1.0 increases it.
    Returns adjusted hex color.
    """
    h, s, l = hex_to_hsl(hex_color)
    s = max(0.0, min(1.0, s * factor))
    return hsl_to_hex(h, s, l)


def adjust_lightness(hex_color, factor):
    """
    Adjust color lightness.
    factor < 1.0 darkens, factor > 1.0 lightens.
    Returns adjusted hex color.
    """
    h, s, l = hex_to_hsl(hex_color)
    l = max(0.05, min(0.95, l * factor))
    return hsl_to_hex(h, s, l)


def adjust_contrast(hex_color, factor):
    """
    Adjust color contrast by pushing lightness away from mid-gray (0.5).
    factor > 1.0 increases contrast, factor < 1.0 decreases it.
    Returns adjusted hex color.
    """
    h, s, l = hex_to_hsl(hex_color)
    if l > 0.5:
        l = 0.5 + (l - 0.5) * factor
    else:
        l = 0.5 - (0.5 - l) * factor
    l = max(0.05, min(0.95, l))
    return hsl_to_hex(h, s, l)


def adapt_color(hex_color, tone='serious'):
    """
    Apply complete tone adaptation to a color.
    tone: serious | creative | data_intensive | educational | promotional
    """
    rules = {
        'serious': {'saturation': 0.7, 'lightness': 1.0, 'contrast': 1.0},
        'creative': {'saturation': 1.2, 'lightness': 1.0, 'contrast': 1.15},
        'data_intensive': {'saturation': 0.85, 'lightness': 1.05, 'contrast': 1.1},
        'educational': {'saturation': 0.9, 'lightness': 1.02, 'contrast': 1.05},
        'promotional': {'saturation': 1.15, 'lightness': 1.0, 'contrast': 1.1},
    }
    rule = rules.get(tone, rules['serious'])
    h, s, l = hex_to_hsl(hex_color)
    s = max(0.0, min(1.0, s * rule['saturation']))
    l = max(0.05, min(0.95, l * rule['lightness']))
    if l > 0.5:
        l = 0.5 + (l - 0.5) * rule['contrast']
    else:
        l = 0.5 - (0.5 - l) * rule['contrast']
    l = max(0.05, min(0.95, l))
    return hsl_to_hex(h, s, l)


def luminance(hex_color):
    """Calculate relative luminance of a color (for contrast ratio)."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
    g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
    b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(hex1, hex2):
    """Calculate WCAG contrast ratio between two colors."""
    l1 = luminance(hex1)
    l2 = luminance(hex2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


if __name__ == '__main__':
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
