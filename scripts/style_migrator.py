#!/usr/bin/env python3
"""
One-shot Style Migration — Extract design DNA from image / URL / text description
and generate a complete design.md for design-driven-pptx.

Usage:
    python style_migrator.py --image ref.jpg --name "my-brand" --output styles/my-brand/design.md
    python style_migrator.py --text "像苹果发布会那样，深色背景配蓝色强调" --name "apple-like" --output styles/apple-like/design.md
    python style_migrator.py --url https://example.com --name "web-ref" --output styles/web-ref/design.md
"""

import sys
import os
import argparse
import re
from pathlib import Path

# Unified color utilities
from color_utils import (
    hex_to_rgb,
    rgb_to_hex,
    hex_to_hsl,
    hsl_to_hex,
    luminance,
    contrast_ratio,
    adjust_lightness,
    ensure_contrast,
    darken_for_contrast,
    classify_palette,
)

# Optional image analysis
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Optional URL fetch
try:
    import urllib.request
    URL_AVAILABLE = True
except ImportError:
    URL_AVAILABLE = False


# ---------------------------------------------------------------------------
# Image color extraction
# ---------------------------------------------------------------------------

def extract_colors_from_image(image_path, n_colors=6):
    """Extract dominant colors from an image using PIL quantize."""
    if not PIL_AVAILABLE:
        raise RuntimeError("Pillow is required for image analysis. Install: pip install Pillow")
    
    img = Image.open(image_path).convert('RGB')
    # Resize for speed
    img = img.resize((128, 128))
    # Quantize to extract palette
    quantized = img.quantize(colors=n_colors, method=Image.Quantize.MEDIANCUT)
    palette = quantized.getpalette()[:n_colors * 3]
    
    colors = []
    for i in range(n_colors):
        r, g, b = palette[i*3], palette[i*3+1], palette[i*3+2]
    # Build histogram in one pass
    hist = quantized.histogram()
    for i in range(n_colors):
        r, g, b = palette[i*3], palette[i*3+1], palette[i*3+2]
        count = hist[i] if i < len(hist) else 0
        colors.append({
            'hex': rgb_to_hex(r, g, b),
            'rgb': (r, g, b),
            'count': count,
            'ratio': count / (128 * 128)
        })
    
    # Sort by count (most frequent first)
    colors.sort(key=lambda c: c['count'], reverse=True)
    return colors


# classify_palette, adjust_lightness, ensure_contrast, darken_for_contrast
# are now imported from color_utils


# ---------------------------------------------------------------------------
# Text description parser
# ---------------------------------------------------------------------------

# Color keyword mapping
COLOR_KEYWORDS = {
    '红': '#E53935', '红色': '#E53935', 'red': '#E53935', 'coral': '#E85D5D', 'crimson': '#DC143C',
    '橙': '#FB8C00', '橙色': '#FB8C00', 'orange': '#FB8C00',
    '黄': '#FDD835', '黄色': '#FDD835', 'yellow': '#FDD835', 'gold': '#FFD700',
    '绿': '#43A047', '绿色': '#43A047', 'green': '#43A047', 'emerald': '#2E7D32',
    '青': '#00897B', '青色': '#00897B', 'teal': '#00897B', 'cyan': '#00BCD4',
    '蓝': '#1E88E5', '蓝色': '#1E88E5', 'blue': '#1E88E5', 'navy': '#1A237E', 'indigo': '#3F51B5',
    '紫': '#8E24AA', '紫色': '#8E24AA', 'purple': '#8E24AA', 'violet': '#7B1FA2',
    '粉': '#EC407A', '粉色': '#EC407A', 'pink': '#EC407A', 'magenta': '#D81B60',
    '黑': '#1A1A1A', '黑色': '#1A1A1A', 'black': '#1A1A1A', 'dark': '#1A1A1A',
    '白': '#FFFFFF', '白色': '#FFFFFF', 'white': '#FFFFFF', 'light': '#F5F5F5',
    '灰': '#9E9E9E', '灰色': '#9E9E9E', 'gray': '#9E9E9E', 'grey': '#9E9E9E',
}

# Background hints
BG_HINTS = {
    '深色': 'dark', 'dark': 'dark', '黑色背景': 'dark', '黑底': 'dark',
    '浅色': 'light', 'light': 'light', '白色背景': 'light', '白底': 'light',
    '暖': 'warm', 'warm': 'warm', '冷': 'cool', 'cool': 'cool',
}

# Typography personality hints
TYPE_HINTS = {
    '苹果': {'display': 'SF Pro Display, Inter', 'body': 'SF Pro Text, Inter', 'personality': 'tech-minimal'},
    'apple': {'display': 'SF Pro Display, Inter', 'body': 'SF Pro Text, Inter', 'personality': 'tech-minimal'},
    '谷歌': {'display': 'Product Sans, Roboto', 'body': 'Roboto, Noto Sans SC', 'personality': 'friendly-tech'},
    'google': {'display': 'Product Sans, Roboto', 'body': 'Roboto, Noto Sans SC', 'personality': 'friendly-tech'},
    '杂志': {'display': 'Playfair Display, Noto Serif SC', 'body': 'Inter, Noto Sans SC', 'personality': 'editorial'},
    'magazine': {'display': 'Playfair Display, Noto Serif SC', 'body': 'Inter, Noto Sans SC', 'personality': 'editorial'},
    '海报': {'display': 'Bebas Neue, Noto Sans SC', 'body': 'Inter, Noto Sans SC', 'personality': 'bold-poster'},
    'poster': {'display': 'Bebas Neue, Noto Sans SC', 'body': 'Inter, Noto Sans SC', 'personality': 'bold-poster'},
    '商务': {'display': 'Montserrat, Noto Sans SC', 'body': 'Open Sans, Noto Sans SC', 'personality': 'professional'},
    'business': {'display': 'Montserrat, Noto Sans SC', 'body': 'Open Sans, Noto Sans SC', 'personality': 'professional'},
    '活泼': {'display': 'Poppins, ZCOOL KuaiLe', 'body': 'Nunito, Yozai', 'personality': 'playful'},
    'playful': {'display': 'Poppins, ZCOOL KuaiLe', 'body': 'Nunito, Yozai', 'personality': 'playful'},
    '复古': {'display': 'Courier Prime, ZCOOL XiaoWei', 'body': 'Courier Prime, Yozai', 'personality': 'retro'},
    'retro': {'display': 'Courier Prime, ZCOOL XiaoWei', 'body': 'Courier Prime, Yozai', 'personality': 'retro'},
}


def parse_text_description(text):
    """Parse a natural language design description into structured features."""
    text_lower = text.lower()
    
    # Extract color keywords
    extracted_colors = []
    for keyword, hex_val in COLOR_KEYWORDS.items():
        if keyword in text or keyword in text_lower:
            extracted_colors.append({'keyword': keyword, 'hex': hex_val})
    
    # Determine background tone
    bg_tone = 'light'
    for hint, tone in BG_HINTS.items():
        if hint in text or hint in text_lower:
            bg_tone = tone
            break
    
    # Determine typography personality
    typography = {'display': 'Bebas Neue, ZCOOL XiaoWei', 'body': 'Inter, Yozai', 'personality': 'modern'}
    for hint, fonts in TYPE_HINTS.items():
        if hint in text or hint in text_lower:
            typography = fonts
            break
    
    # Build color palette from extracted colors
    colors = {}
    if extracted_colors:
        # Determine primary from extracted colors (highest saturation or first)
        by_sat = sorted(extracted_colors, key=lambda c: hsl(c['hex'])[1], reverse=True)
        colors['primary'] = by_sat[0]['hex']
        colors['primaryDark'] = adjust_lightness(colors['primary'], 0.85)
        
        # Background based on tone hint explicitly
        if bg_tone == 'dark':
            # Dark theme: use dark background, never the primary color
            colors['background'] = '#121212'
            colors['ink'] = '#FFFFFF'
            colors['text'] = '#A0A0A0'
            colors['textLight'] = '#707070'
            colors['white'] = '#FFFFFF'
            colors['surfaceAlt'] = '#1E1E1E'
        elif bg_tone == 'light':
            colors['background'] = '#F5F5F5'
            colors['ink'] = '#1A1A1A'
            colors['text'] = '#6B6B6B'
            colors['textLight'] = '#B0B0B0'
            colors['white'] = '#FFFFFF'
            colors['surfaceAlt'] = '#E8E8E8'
        else:
            # Auto-detect from second color if available
            if len(extracted_colors) > 1:
                second = extracted_colors[1]['hex']
                lum = luminance(second)
                if lum > 0.7:
                    colors['background'] = second
                    colors['ink'] = '#1A1A1A'
                    colors['text'] = '#6B6B6B'
                    colors['textLight'] = '#B0B0B0'
                    colors['white'] = '#FFFFFF'
                    colors['surfaceAlt'] = adjust_lightness(second, 0.92)
                else:
                    colors['background'] = '#F5F5F5'
                    colors['ink'] = second if lum < 0.25 else '#1A1A1A'
                    colors['text'] = '#6B6B6B'
                    colors['textLight'] = '#B0B0B0'
                    colors['white'] = '#FFFFFF'
                    colors['surfaceAlt'] = '#E8E8E8'
            else:
                colors['background'] = '#F5F5F5'
                colors['ink'] = '#1A1A1A'
                colors['text'] = '#6B6B6B'
                colors['textLight'] = '#B0B0B0'
                colors['white'] = '#FFFFFF'
                colors['surfaceAlt'] = '#E8E8E8'
    # Ensure derived colors are present
    if 'surface' not in colors:
        bg_lum = luminance(colors['background'])
        if bg_lum > 0.5:
            colors['surface'] = adjust_lightness(colors['background'], 0.96)
            colors['surfaceAlt'] = adjust_lightness(colors['background'], 0.92)
        else:
            colors['surface'] = adjust_lightness(colors['background'], 1.08)
            colors['surfaceAlt'] = adjust_lightness(colors['background'], 1.15)
    if 'primaryDark' not in colors:
        colors['primaryDark'] = adjust_lightness(colors['primary'], 0.85)
    if 'primaryText' not in colors:
        colors['primaryText'] = colors['primary']

    return {
        'colors': colors,
        'typography': typography,
        'bg_tone': bg_tone,
        'extracted_colors': extracted_colors,
    }


# ---------------------------------------------------------------------------
# design.md generator
# ---------------------------------------------------------------------------

def generate_design_md(name, colors, typography, mood='modern', bucket='professional'):
    """Generate a complete design.md string."""
    
    # Determine aesthetic bucket from personality
    personality = typography.get('personality', 'modern')
    bucket_map = {
        'tech-minimal': 'professional',
        'friendly-tech': 'professional',
        'editorial': 'editorial',
        'bold-poster': 'bold',
        'professional': 'professional',
        'playful': 'playful',
        'retro': 'retro',
    }
    bucket = bucket_map.get(personality, bucket)
    
    # Get decoration grammar based on bucket
    decorations = {
        'editorial': [
            'Oversized serif drop-cap numeral at 0.10–0.14 opacity behind section titles',
            'Thin elegant rule (1–2px) in the accent color as a horizontal divider',
            'Subtle texture overlay at 0.03–0.06 opacity on featured surfaces',
        ],
        'bold': [
            '45° diagonal hatch or geometric line overlay on accent-colored regions (opacity 0.06)',
            'Oversized decorative numeral at 0.12 opacity behind titles or stat callouts',
            'Thick accent border (4–5px) on cards, sidebars, or panel edges',
            'Hard-edge color block in a corner or edge as a compositional anchor',
        ],
        'playful': [
            'One organic blob frame per slide in an unused corner (asymmetric border-radius, 3px stroke)',
            'One 2px-stroke scribble per slide (squiggle, star, or arrow) in a margin',
            'Small doodle circle or slightly rotated rectangle (5–10°) as a corner accent',
        ],
        'retro': [
            'L-shaped pixel corner brackets (4px stroke, neon or accent color) framing cards',
            'CRT scanline overlay on dark backgrounds (0.04 opacity)',
            'Pixel-grid background pattern (40px grid, 0.07 opacity) on dark or colored surfaces',
        ],
        'professional': [
            'Thin accent line (1–2px) under titles or as a section divider in the primary accent color',
            'Subtle gradient overlay (light-to-transparent) on cards or panels for gentle depth',
            'Minimal geometric shape (circle, square, or line) in a corner at low opacity',
        ],
    }
    deco_items = decorations.get(bucket, decorations['professional'])
    deco_text = '\n'.join([f'    - "{d}"' for d in deco_items])
    
    # Font sizing based on personality
    if personality in ('bold-poster', 'playful'):
        hero_size, section_size, card_size = 72, 52, 32
        line_height = 1.0
        tracking = 4
    elif personality == 'editorial':
        hero_size, section_size, card_size = 56, 42, 28
        line_height = 1.1
        tracking = 2
    elif personality == 'retro':
        hero_size, section_size, card_size = 48, 36, 24
        line_height = 1.2
        tracking = 1
    else:  # tech-minimal, professional, friendly-tech
        hero_size, section_size, card_size = 64, 48, 28
        line_height = 1.05
        tracking = 3
    
    display_font = typography.get('display', 'Bebas Neue, ZCOOL XiaoWei')
    body_font = typography.get('body', 'Inter, Yozai')
    
    # CJK adaptation
    cjk_display = display_font.split(',')[-1].strip() if ',' in display_font else 'ZCOOL XiaoWei'
    cjk_body = body_font.split(',')[-1].strip() if ',' in body_font else 'Yozai'
    
    md = f"""# Design System: {name}

## Color System

```yaml
colors:
  primary: "{colors['primary']}"
  primaryDark: "{colors['primaryDark']}"
  primaryText: "{colors.get('primaryText', colors['primary'])}"
  background: "{colors['background']}"
  surface: "{colors['surface']}"
  surfaceAlt: "{colors['surfaceAlt']}"
  ink: "{colors['ink']}"
  text: "{colors['text']}"
  textLight: "{colors['textLight']}"
  white: "{colors['white']}"
```

## Typography

```yaml
textStyles:
  heroTitle:
    fontSize: {hero_size}
    color: "$ink"
    fontFamily: "{display_font}"
    lineHeight: {line_height}
    letterSpacing: {tracking}
  sectionHeadline:
    fontSize: {section_size}
    color: "$ink"
    fontFamily: "{display_font}"
    lineHeight: {line_height}
    letterSpacing: {max(1, tracking // 2)}
  columnTitle:
    fontSize: {card_size}
    color: "$ink"
    fontFamily: "{display_font}"
    lineHeight: 1.1
    letterSpacing: {max(1, tracking // 2)}
  cardTitle:
    fontSize: 24
    color: "$ink"
    fontFamily: "{display_font}"
    lineHeight: 1.1
    letterSpacing: 1
  statNumeral:
    fontSize: 56
    color: "$primary"
    fontFamily: "{display_font}"
    lineHeight: 1.0
  body:
    fontSize: 18
    color: "$text"
    fontFamily: "{body_font}"
    lineHeight: 1.7
  bodySm:
    fontSize: 15
    color: "$text"
    fontFamily: "{body_font}"
    lineHeight: 1.6
  sectionLabel:
    fontSize: 12
    color: "$primary"
    fontFamily: "{body_font}"
    lineHeight: 1.0
    letterSpacing: 4
```

## Table Styles

```yaml
tableStyles:
  default:
    fontSize: 15
    fontFamily: "{body_font}"
    headerFill: "$primary"
    headerColor: "$white"
    headerBold: true
    bodyFill: ["$white", "$background"]
    bodyColor: "$ink"
    border:
      style: solid
      width: 2
      color: "$ink"
```

## Decoration Grammar

decoration-grammar:
  count-per-slide: "1–3 decorations maximum"
  placement:
    - "Place in corners or edges that the primary content does not occupy"
    - "Offset 20–40px from canvas edges"
    - "Never place over text or in the center of the slide"
  size-range: "30–80px in the largest dimension"
  density:
    cover: "2–3 decorations"
    chapter: "2–3 decorations"
    content: "1–2 decorations"
    final: "1–2 decorations"
  style-specific:
{deco_text}

## CJK Adaptation

| Latin Font | CJK Fallback | Role |
|------------|-------------|------|
| {display_font.split(',')[0].strip()} | {cjk_display} | Display / Headlines |
| {body_font.split(',')[0].strip()} | {cjk_body} | Body / UI |

## Notes

- **Mood**: {mood}
- **Personality**: {personality}
- **Aesthetic Bucket**: {bucket}
- **Generated by**: style_migrator.py
"""
    return md


# ---------------------------------------------------------------------------
# URL analysis (simplified)
# ---------------------------------------------------------------------------

def fetch_and_analyze_url(url):
    """Fetch URL and attempt basic color extraction from CSS."""
    if not URL_AVAILABLE:
        raise RuntimeError("urllib is not available for URL fetching")
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        raise RuntimeError(f"Failed to fetch URL: {e}")
    
    # Extract color-like hex values from CSS
    hex_pattern = r'#[0-9A-Fa-f]{{3,6}}\b'
    colors_found = re.findall(hex_pattern, html)
    
    # Normalize and count
    color_counts = {}
    for c in colors_found:
        c = c.upper()
        if len(c) == 4:  # #RGB -> #RRGGBB
            c = '#' + c[1]*2 + c[2]*2 + c[3]*2
        color_counts[c] = color_counts.get(c, 0) + 1
    
    # Filter out common grays and whites
    filtered = {k: v for k, v in color_counts.items() 
                if k not in ('#FFFFFF', '#000000', '#EEEEEE', '#DDDDDD', '#CCCCCC', '#BBBBBB', '#AAAAAA', '#999999', '#888888', '#777777', '#666666', '#555555', '#444444', '#333333', '#222222', '#111111')}
    
    if not filtered:
        filtered = color_counts
    
    # Take top 5
    top_colors = sorted(filtered.items(), key=lambda x: x[1], reverse=True)[:5]
    palette = [{'hex': c, 'count': n, 'ratio': n / sum(v for _, v in top_colors)} for c, n in top_colors]
    
    return palette


# ---------------------------------------------------------------------------
# Main CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='One-shot Style Migration for design-driven-pptx')
    parser.add_argument('--image', help='Path to reference image')
    parser.add_argument('--url', help='URL of reference website')
    parser.add_argument('--text', help='Natural language design description')
    parser.add_argument('--name', required=True, help='Style name (used for output directory and design system name)')
    parser.add_argument('--output', help='Output path for design.md (default: styles/{name}/design.md)')
    parser.add_argument('--mood', default='modern', help='Design mood (modern, bold, playful, retro, editorial)')
    
    args = parser.parse_args()
    
    if not any([args.image, args.url, args.text]):
        parser.error("At least one of --image, --url, or --text is required")
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path('styles') / args.name / 'design.md'
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Extract features based on input type
    if args.image:
        print(f"Analyzing image: {args.image}")
        colors_data = extract_colors_from_image(args.image)
        print(f"  Extracted {len(colors_data)} dominant colors")
        for c in colors_data[:5]:
            print(f"    {c['hex']} — {c['ratio']*100:.1f}%")
        colors = classify_palette(colors_data)
        typography = {'display': 'Bebas Neue, ZCOOL XiaoWei', 'body': 'Inter, Yozai', 'personality': 'modern'}
        
    elif args.url:
        print(f"Fetching URL: {args.url}")
        palette = fetch_and_analyze_url(args.url)
        print(f"  Found {len(palette)} colors from CSS")
        for c in palette:
            print(f"    {c['hex']} — {c['ratio']*100:.1f}%")
        # Convert to classify_palette format
        colors_data = [{'hex': c['hex'], 'rgb': hex_to_rgb(c['hex']), 'count': c['count'], 'ratio': c['ratio']} for c in palette]
        colors = classify_palette(colors_data)
        typography = {'display': 'Inter, Noto Sans SC', 'body': 'Inter, Noto Sans SC', 'personality': 'modern'}
        
    else:  # text description
        print(f"Parsing description: {args.text}")
        features = parse_text_description(args.text)
        colors = features['colors']
        typography = features['typography']
        print(f"  Detected colors: {list(colors.keys())}")
        print(f"  Typography personality: {typography['personality']}")
        print(f"  Background tone: {features['bg_tone']}")
    
    # Generate design.md
    design_md = generate_design_md(args.name, colors, typography, mood=args.mood)
    
    # Write output
    output_path.write_text(design_md, encoding='utf-8')
    print(f"\n✅ Design system generated: {output_path}")
    print(f"   Primary: {colors['primary']}")
    print(f"   Background: {colors['background']}")
    print(f"   Ink: {colors['ink']}")
    print(f"   Personality: {typography['personality']}")
    
    # Also print summary for copy-paste
    print(f"\n--- Quick Start ---")
    print(f"python scripts/pptd2pptx.py your.pptd --style {args.name}")


if __name__ == '__main__':
    main()
