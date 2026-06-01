# Font System

## Selection Principles

1. Language matching: When the user's query is in Chinese or requests a Chinese PPT, both Chinese and English fonts need to be specified; otherwise, only English fonts need to be set.
2. Selection approach: It is recommended to prioritize highly readable fonts for body text, and use stylized fonts + special design treatments (all caps, expanded letter spacing, bold, italic, etc.) for titles or special pages to enhance the style.
3. The font combination should support the overall visual style positioning.
4. Name consistency: **Make sure the font name is exactly consistent, including capitalization and spaces, to ensure the model can use it correctly.**
5. Dual-font format: Use `"Latin, CJK"` format for CJK content, e.g., `"Inter, Noto Sans SC"`. The converter automatically injects `a:ea` elements for CJK fallback.

## Font List

### English Fonts

| Font Name | Font Type | Style & Characteristics | Use Cases | Stylized Font |
|---|---|---|---|---|
| Liter | Sans-serif | Modern neo-grotesque style, low contrast, well-proportioned, optimized for screen display, clean and rational | Technology, product | No |
| HedvigLettersSans | Sans-serif | "Non-designer perspective" design, slightly irregular, distinctive personality, strong brand identity | Creative design, branding | No |
| Oranienbaum | Serif | Modern high-contrast serif, strong geometric feel, elegant lines, classical temperament | Culture, art, fashion | No |
| QuattrocentoSans | Sans-serif | Classic elegant sans-serif, gentle, highly readable, clear at small sizes | Academic, corporate, education | No |
| SortsMillGoudy | Serif | Revival of Goudy Old Style with classical print aesthetics, soft serifs, excellent readability | Literature, humanities | No |
| Unna | Serif | Neoclassical serif, pronounced vertical rhythm, elegance with strength | Literature, publishing, academic | Yes |
| Coda | Sans-serif | Rounded and friendly, soft curves, high openness | Business, friendly brand tone | Yes |
| Jersey15 | Sans-serif (sporty) | Sports jersey style, structured and square, pronounced grid feel (English + numbers only) | Sports, tech showcase pages | Yes |
| Jersey20Charted | Pixel font (gridded) | Sports number style with gridded texture overlay, enhanced athletic texture (English + numbers only) | Sports, mechanical, decorative showcase pages | Yes |
| **Inter** | Sans-serif | Highly legible neo-grotesque, optimized for UI, extensive weight range | Technology, corporate, general | No |
| **Space Grotesk** | Sans-serif | Quirky grotesque with geometric proportions, distinctive letterforms | Creative tech, branding, editorial | No |
| **Bebas Neue** | Sans-serif (condensed) | All-caps condensed display font, bold and impactful | Posters, headlines, sports | Yes |
| **Bodoni Moda** | Serif (high-contrast) | Extreme contrast between thick and thin strokes, elegant and luxurious | Fashion, luxury, editorial | Yes |
| **Poppins** | Sans-serif | Geometric sans-serif with warm personality, excellent for display | Playful, modern, friendly | No |
| **Montserrat** | Sans-serif | Urban geometric sans-serif, versatile and contemporary | Business, general purpose | No |
| **Playfair Display** | Serif (transitional) | High-contrast transitional serif, sophisticated editorial feel | Magazines, luxury, culture | Yes |
| **Product Sans** | Sans-serif | Google's brand font, geometric and friendly | Tech, friendly brand tone | No |
| **Open Sans** | Sans-serif | Humanist sans-serif, extremely versatile and readable | General purpose, web, corporate | No |
| **SF Pro Display/Text** | Sans-serif | Apple's system font, refined and modern | Tech, minimal, Apple-style | No |
| **Roboto** | Sans-serif | Google's system font, mechanical yet friendly | Android, tech, general | No |
| **Courier Prime** | Monospace | Enhanced Courier for screen, classic typewriter aesthetic | Retro, code, editorial | No |
| **Syne** | Sans-serif | Art gallery font, unusual proportions, avant-garde | Creative, artistic, experimental | Yes |
| **Nunito** | Sans-serif | Rounded sans-serif, soft and friendly | Playful, children's, casual | No |
| **MS Sans Serif** | Sans-serif | Classic Windows 9x system font, pixel-perfect retro feel | Retro, nostalgic, UI mockups | No |
| **Segoe UI** | Sans-serif | Microsoft's modern system font, clean and professional | Windows-style, corporate | No |

### Chinese Fonts

| Font Name | Font Type | Style & Characteristics | Use Cases | Usage Restrictions |
|---|---|---|---|---|
| MiSans | Sans-serif (Hei) | Xiaomi system font, clean and modern, variable weight, excellent screen rendering (multilingual support) | Technology, corporate, product | No |
| Noto Sans SC | Sans-serif (Hei) | Source Han Sans fork, well-structured, neutral style, extremely wide coverage. **Due to widespread use, please use sparingly** | Report-style | No |
| Noto Serif SC | Serif (Song) | Source Han Serif, refined Song structure, contrasting strokes, elegant reading experience | Literature, design, formal presentations | No |
| siyuanSongti | Serif (Song) | Source Han Serif, refined Song structure, contrasting strokes, elegant reading experience (multilingual support) | Literature, design, formal presentations | No |
| alimamadaoliti | Calligraphic (Lishu) | Alibaba Dao Li Ti, clerical script style, sharp brush strokes, combining strength with archaic charm | Chinese traditional style, culture, art exhibitions | No |
| alimamadongfangdakai | Calligraphic (Kai) | Alibaba Dongfang Da Kai, based on Yan-style calligraphy, full and rounded, bold and powerful | Culture, brand launches, Chinese traditional style | No |
| alimamashuheiti | Sans-serif (Hei) | Alibaba Shu Hei Ti, geometric sans-serif, uniform and structured, strong commercial feel | Business, technology, e-commerce | No |
| zhankuwenyiti | Handwritten | Zhanku Wenyi Ti, clean and fresh, slightly handwritten feel, strong artistic atmosphere | Light design, lifestyle | No |
| feibozhengdianti | Calligraphic (Brush) | Feibo Zhengdian Ti, brush writing style, heavy strokes, powerful | Film posters, e-commerce, brand showcase | No |
| deyihei | Sans-serif (Oblique Hei) | Deyi Hei, slender oblique sans-serif, combining humanist and geometric qualities, strong modern feel. **Does not support non-italic** | Creative technology, brand showcase | No |
| xiawuxinzhisong | Serif (Song) | LXGW Xin Zhi Song, based on IPAmj Mincho, bright, elegant, well-structured | Literature, classical style, print style | No |
| **Yozai** | Sans-serif (Hei) | Modern geometric Chinese sans-serif, clean and structured | General purpose, technology, body text | No |
| **ZCOOL XiaoWei** | Handwritten | Light handwritten style, delicate and artistic | Light design, lifestyle, creative | No |

### Mixed CJK-Latin Fonts

| Font Name | Font Type | Style & Characteristics | Use Cases | Usage Restrictions |
|---|---|---|---|---|
| jingpindianzhenTi | Pixel font | Jingpin Pixel Font, 9x9 dot matrix pixel style, strong retro electronic feel | Games, technology, pixel art | Yes |
| LXGW Bright | Serif (Fangsong/Kai) | LXGW Bright, combining Fangsong and Kai characteristics, gentle and clear letterforms | Literature, education, humanities | No |
| ZCOOL KuaiLe | Handwritten (Rounded) | Zhanku KuaiLe, lively and cute, playful and cartoon-like, youthful and energetic | Animation, children's, entertainment | No |

## Font Pairing Reference

| Visual Style | Latin Display | Latin Body | CJK Display | CJK Body |
|---|---|---|---|---|
| Tech Minimal | SF Pro Display, Inter | SF Pro Text, Inter | MiSans | MiSans |
| Editorial | Playfair Display, Bodoni Moda | Liter, SortsMillGoudy | Noto Serif SC | Noto Serif SC |
| Bold Poster | Bebas Neue | Inter, Open Sans | ZCOOL XiaoWei | Yozai |
| Playful | Poppins, Syne | Nunito | ZCOOL KuaiLe | Yozai |
| Professional | Montserrat, Space Grotesk | Inter, Open Sans | MiSans | MiSans |
| Retro | Courier Prime | Courier Prime | ZCOOL XiaoWei | Yozai |
| Business | QuattrocentoSans | QuattrocentoSans | Noto Sans SC | Noto Sans SC |
