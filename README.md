# Design-Driven PPTX

> **AI-powered presentation generator that turns a visual design system + content source into production-ready `.pptx` files through an intermediate `.pptd` format.**
>
> **基于视觉设计系统 + 内容源的 AI 驱动演示文稿生成器，通过中间格式 `.pptd` 输出生产级 `.pptx`。**

---

## 核心链路 / Core Pipeline

```
内容源 (docx/大纲)          视觉设计系统 (design.md)
    │                              │
    └──────────┬───────────────────┘
               ▼
        ┌─────────────┐
        │  AI 多智能体  │  ← 主 agent 设计主题 + 大纲 + .pptd
        │  生成 .pptd  │  ← Subagent 并行构建 .page 文件
        └─────────────┘
               │
               ▼
        ┌─────────────┐
        │  PPTD 转换器  │  ← python-pptx 引擎
        │  导出 .pptx  │
        └─────────────┘
               │
               ▼
         可编辑的 PPTX
```

---

## 特性 / Features

| 特性 | Feature | 说明 |
|------|---------|------|
| 设计系统驱动 | Design-system driven | 基于 `design.md` 视觉规范生成，保证风格一致性 |
| 多智能体并行 | Multi-agent parallel | 主 agent 完成设计 + 大纲，subagent 并行构建页面 |
| 内容零增删 | Zero content mutation | 严格忠实原始文档，禁止增删改 |
| 丰富组件库 | Rich component library | 支持文本、形状、图片、表格、图表、图标 |
| 富文本支持 | Rich text support | `<p>`, `<span>`, `<strong>`, `<em>`, `<a>`, 列表等 |
| 真实图表 | Real charts | 柱状图、折线图、饼图、条形图，支持系列样式（平滑曲线、线型、标记点） |
| Layer 分层 | Z-Order layers | 显式 `layer` 字段（-1~2），背景/容器/内容/前景自动排序 |
| CJK 字体回退 | CJK font fallback | 拉丁字体 + CJK 字体双声明，自动注入 `a:ea` 元素 |
| 自由形状 | Freeform paths | SVG 路径语法（M/L/C/Q/Z），支持旋转与填充 |
| 一键转 PPTX | One-click to PPTX | 内置 `pptd2pptx.py` 转换器，本地即可导出 |
| **🎨 风格迁移** | **One-shot Style Migration** | 上传图片或输入描述，自动提取设计 DNA 生成 `design.md` |
| **📊 语义可视化** | **Semantic Auto-Viz** | 自动识别内容中的数据模式，插入图表/时间线/表格 |
| **📝 设计透明** | **Design Rationale** | 自动生成每页的设计决策说明文档 |

---

> 建议在 [Kimi Code] 中运行本 Skill。

---

## 依赖 / Dependencies

运行本 Skill 的转换器需要以下 Python 库：

```bash
pip install python-pptx pyyaml
```

或直接从项目根目录安装：

```bash
pip install -r requirements.txt
```

| 库 | 用途 |
|----|------|
| `python-pptx` | 生成 `.pptx` 文件 |
| `PyYAML` | 解析 `.pptd` / `.page` 的 YAML 格式 |

> 注：AI 生成 `.pptd` 阶段无需安装任何依赖，纯文本/YAML 操作。

---

## 快速开始 / Quick Start

### 1. 准备输入 / Prepare Inputs

将内容文档（`.docx` 或 `.md` 大纲）和视觉设计系统（`design.md`）放入工作目录：

```
my-presentation/
├── design.md          # 视觉设计系统（颜色、字体、布局、组件）
├── outline.md         # 内容大纲（可选，AI 也可生成）
└── content.docx       # 原始内容文档
```

> 本项目 `styles/` 目录已内置 **35 套**设计系统，涵盖粗野主义、编辑风、复古风、海报风、新拟态等多种视觉语言，详见下方「可选风格」章节。

### 2. 生成 PPTD / Generate PPTD

按 SKILL 工作流执行（主 agent 完成设计适配 + 大纲 + `.pptd` 主文件，然后分派 subagent 并行构建 `.page` 文件）：

```bash
# 主 agent 步骤：
# 1. 读取 design.md + 内容源
# 2. 适配为 PPTD Theme（参考 references/design-adapter.md）
# 3. 创建 outline.md
# 4. 创建 <name>.pptd 主文件
# 5. 分派 subagent 并行构建 pages/*.page
# 6. 运行 check & fix
# 7. 交付 .pptd 项目
```

### 3. 转换为 PPTX / Convert to PPTX

```bash
python3 scripts/pptd2pptx.py my-presentation/slides.pptd my-presentation/slides.pptx
```

### 4. 惊艳增强（可选）/ Wow Enhancements (Optional)

```bash
# 🎨 One-shot 风格迁移 — 从图片/描述生成设计系统
python3 scripts/style_migrator.py --image brand-poster.jpg --name "my-brand"
python3 scripts/style_migrator.py --text "像苹果发布会那样，深色背景配蓝色强调" --name "apple-like"

# 📊 语义自动可视化 — 智能识别数据并插入图表
python3 scripts/auto_visualizer.py --pptd my-presentation/slides.pptd --mode enhance

# 📝 设计决策透明化 — 生成设计理由文档
python3 scripts/design_rationale.py --pptd my-presentation/slides.pptd --design-md my-presentation/design.md
```

---

## 项目结构 / Project Structure

```
design-driven-pptx/
├── SKILL.md                          # Skill 定义与工作流说明
├── README.md                         # 本文件
├── scripts/
│   ├── check.sh                      # PPTD 校验脚本（自动回退到 Python）
│   ├── check_pptd.py                 # 纯 Python PPTD 校验器（10+ 规则 + 布局质量检查）
│   ├── pptd2pptx.py                  # PPTD → PPTX 转换器
│   ├── style_migrator.py             # 🎨 One-shot 风格迁移（图片/URL/描述 → design.md）
│   ├── auto_visualizer.py            # 📊 语义自动可视化（内容 → chart/table/timeline）
│   └── design_rationale.py           # 📝 设计决策透明化（.pptd → 设计理由文档）
├── styles/                           # 内置设计系统库（35 套）
│   ├── block-frame/
│   │   └── design.md
│   ├── blue-professional/
│   │   └── design.md
│   └── ...
├── format/
│   └── pptd.md                       # PPTD 文件格式规范
├── references/
│   ├── design-adapter.md             # design.md → PPTD Theme 映射指南
│   ├── main-agent-workflow.md        # 主 agent 工作流
│   └── subagent-prompts.md           # Subagent 提示词模板
├── guideline/
│   ├── design/
│   │   └── profiles/                 # 场景画像（学术/商业/教育/推广等）
│   └── subagent/
│       └── attention.md              # Subagent 注意事项
└── assets/
    └── outline-template.md           # 大纲模板
```

---

## PPTD 格式 / PPTD Format

PPTD（Presentation Data）是一种基于 YAML 的中间表示格式，用于在 AI 生成阶段精确控制演示文稿的结构与样式。

- **主文件** `.pptd`：定义 `title`, `size`, `theme`, `pages` 列表
- **页面文件** `.page`：每页独立 YAML，包含 `pageType`, `background`, `elements`
- **坐标系统**：`bounds: [x, y, w, h]`，画布尺寸默认 `1280 × 720`

详见 `format/pptd.md`。

---

## 可选风格 / Available Styles

`styles/` 目录下每套设计系统均包含完整的 `design.md`，定义颜色、字体、组件、布局与 CJK 适配规则。使用时指定文件夹名称即可。

### 粗野主义 / Brutalist

| 风格名 | 关键词 | 简介 |
|--------|--------|------|
| `block-frame` | 新粗野主义、糖果色、硬阴影 | 4px 纯黑边框 + 8px 硬偏移阴影 + 五种高饱和粉彩（粉/蓝/绿/黄/奶油），Inter 900 大写标题 + Space Grotesk 标签，倾斜装饰元素故意刺破网格 |
| `raw-grid` | 系统原生、极简边框、粉彩 | 3px 实线黑边框即布局，系统默认无衬线字体 900 权重，白底 + 黑结构 + 腮红粉/鼠尾草绿两种 muted pastel |
| `creative-mode` | 新粗野主义、四色强调、海报感 | 暖奶油底 + 森林绿/热粉/焦橙/阳光黄四色强调，Archivo Black 大写标题，无圆角无渐变，Bauhaus 网格 + 朋克杂志混合 |

### 编辑风 / Editorial

| 风格名 | 关键词 | 简介 |
|--------|--------|------|
| `biennale-yellow` | 艺术双年展、文学、克制 | 暖羊皮纸底 + 柔光太阳黄放射渐变 + 深靛蓝墨水色，Instrument Serif 高对比衬线 + Archivo 无衬线，无阴影无边框，仅有 1px 发线 |
| `cartesian` | 博物馆图录、建筑、安静 | Playfair Display 衬线标题 + Inter 正文，暖石色五色调色板，几何线装饰（细圆、虚线弧、发线），Massimo Vignelli 式编辑感 |
| `editorial-forest` | 文学季刊、艺术专著、森林绿 | Source Serif 4 衬线 + 深森林绿/灰玫瑰粉/燕麦奶油三色，JetBrains Mono 编辑标签，纸张质感 |
| `editorial-tri-tone` | 独立出版物、三色限制、文学 | 严格三色：腮红粉 + 金黄奶油 + 深酒红，Bricolage Grotesque 标题 + Instrument Serif 斜体强调 + JetBrains Mono 元数据 |
| `emerald-editorial` | 时尚封面、戏剧感、祖母绿 | Bodoni Moda 900 权重衬线 + 饱和祖母绿底 + 深海军蓝墨水，双层线装饰括号，Harper's Bazaar / Vogue 封面感 |
| `grove` | 文学期刊、品牌书、安静权威 | Playfair Display 400（从不加粗）+ Jost 300 正文 + JetBrains Mono 标签，深森林绿底 + 暖奶油字 + 赤陶珊瑚强调 |
| `monochrome` | 单色、学术专著、极轻字重 | Jost 200–300 超轻几何无衬线 + Lora 斜体衬线 + JetBrains Mono，黑墨水在奶油纸上，无彩色强调 |
| `signal` | 经济学人、情报简报、贵族感 | Source Serif 4 标题（罗马/斜体混排古董金）+ DM Sans 正文 + IBM Plex Mono 时间戳，暖奶油纸 + 深编辑海军蓝 + 古董金强调 |
| `soft-editorial` | 杂志跨页、riso 印刷、柔和 | Cormorant Garamond 衬线 + Work Sans 正文，奶油纸 + 四色 pastel 糖果卡片（粉/柠檬黄/桃/鼠尾草），大圆角 |
| `vellum` | 画廊展墙、单色、静止 | 深长春花蓝底 + 暖黄绿字，斜体 Cormorant Garamond 为唯一人格，Courier Prime 为钉注注释，一色两面，零动态 |

### 海报风 / Poster

| 风格名 | 关键词 | 简介 |
|--------|--------|------|
| `bold-poster` | 意大利体育杂志、大字报、番茄红 | Shrikhand 厚重展示字体（200–320px 常倾斜）+ Libre Baskerville 文学正文 + Space Grotesk 标签，白底 + 深棕黑墨水 + 饱和番茄红 |
| `broadside` | 抗议海报、橙色宣言、大字 | Barlow 900 权重超大写 lowercase（~187px），深/橙双色系统，单 loud 色 + 零装饰，Wim Crouwel 网格精神 |
| `neo-grid-bold` | 编辑海报、霓虹黄、12列网格 | Space Grotesk 700 严格大写 + JetBrains Mono 标签，灰泥黄/墨水黑/电柠檬黄三色面板交替，当代编辑印刷 + 野兽派年报感 |
| `peoples-platform` | WPA海报、政治运动、民众主义 | Alfa Slab One 压缩粗衬线 + Caveat Brush 手写体 + DM Mono 元数据，电钴蓝/琥珀橙/热红三色，纸张颗粒覆盖 |
| `stencil-tablet` | 滑板海报、模板印刷、工业风 | Stardos Stencil 模板字体 + Barlow Condensed 元数据 + Inter 正文，骨色/黑色 + 七色复古印刷强调（赭/洋红/橙/青/蓝/芥末/橄榄），圆角平板卡片 |
| `studio` | 设计工作室、字即图形、黄黑反转 | Barlow 900 超大写（字即形状），近黑底 + 酸黄字 + 黄底黑字反转，IBM Plex Mono 页脚，无阴影无圆角 |

### 复古风 / Retro

| 风格名 | 关键词 | 简介 |
|--------|--------|------|
| `8-bit-orbit` | 16位街机、像素、CRT扫描线 | Tektur 几何显示字体 + Chakra Petch 正文 + Space Mono 标签，深宇宙海军蓝 + 青/热粉/黄三色霓虹，4px 硬偏移阴影 + CRT 扫描线 + 星场 |
| `retro-windows` | Win95/98、窗口UI、怀旧 | MS Sans Serif + Press Start 2P 像素字体 + VT323 终端字体，Win9x 系统色（灰按钮/海军标题栏/白凹陷输入框），软件UI风 |
| `retro-zine` | 独立出版、riso印刷、运动海报 | Bebas Neue  condensed 工业无衬线 + Space Grotesk 正文 + Caveat 手写，暖卡其纸 + 深森林绿 + 墨水黑，SVG 颗粒覆盖 |

### 趣味风 / Playful

| 风格名 | 关键词 | 简介 |
|--------|--------|------|
| `capsule` | 药丸形容器、糖果色、杂志度假 | Bodoni Moda 衬线标题 + Space Grotesk 正文，日晒奶油底 + 九色糖果 palette，9999px 圆角药丸 + 2px 墨水描边 + 软阴影，Memphis-meets-editorial |
| `daisy-days` | 儿童故事书、贴纸、手绘 | Fredoka One 块状展示字体 + Quicksand 圆润人文无衬线，阳光花园 palette（青绿/柔粉/黄油黄/薄荷/薰衣草），手绘 SVG 装饰（雏菊/星星/太阳/云/彩虹）|
| `pin-and-paper` | 便签纸、安全别针、手写注释 | 黄色便签纸 + 深钴蓝墨水，Caveat 手写注释 + Space Grotesk 标题 + DM Mono 档案标签，分形噪点纸张纹理 + 手绘安全别针 SVG |
| `playful` | 独立工作室、riso杂志、手绘涂鸦 | Syne 700–800 展示字体 + Space Grotesk 正文，桃土色底 + 炭墨色墨水，有机 blob 框 + 涂鸦 + 双描边偏移边框 |
| `sakura-chroma` | 磁带包装、日本印刷目录、工业编辑 | Big Shoulders Display 压缩工业展示 + Albert Sans 正文 + JetBrains Mono 标签 + Noto Sans JP，暖奶油纸 + 六色主 palette + 暖棕墨水，花瓣簇/彩带/星形章 |
| `scatterbrain` | 便利贴、软木板、创意工作坊 | Shrikhand 装饰衬线 + Zilla Slab 友好粗衬线 + Caveat 手写，pastel 便利贴色（黄/蓝/粉/绿/橙/紫）在奶油纸/软木/渐变背景上，红图钉/胶带/阴影组合 |

### 专业/商务风 / Professional

| 风格名 | 关键词 | 简介 |
|--------|--------|------|
| `blue-professional` | 咨询级、金融、稳重 | 暖奶油底 + 单一饱和钴蓝强调，Space Grotesk 标题 + Inter 正文，4% 透明度钴蓝卡片 + 1.5px 半透明边框 + 10–14px 圆角，McKinsey 级简报感 |
| `cobalt-grid` | 日本杂志、趋势报告、方格纸 | Newsreader 衬线大标题 + DM Mono 标签，暖奶油纸 + 电钴蓝墨水 + 永久方格纸背景，像素故障柱 + QR 式 8×8 网格补丁，WIRED Japan 感 |
| `coral` | 旅行海报、Saul Bass、运动杂志 | Bebas Neue condensed 大写 + Inter 正文，珊瑚火/墨水黑/暖奶油三色，45° 对角 hatch 图案，中世纪旅行海报 + Saul Bass 电影标题 |
| `long-table` | 晚餐俱乐部海报、riso印刷、小批量 | 单一铁锈赤陶色墨水 + 黄油奶油纸，Bricolage Grotesque 700–800 大写标题 + Fraunces 衬线正文，药丸按钮/轮廓徽章/斜体版号/虚线边框 |
| `mat` | 高端产品落地页、材料触感、深绿 | Bricolage Grotesque 展示 + DM Sans 正文 + DM Mono 标签，深森林绿环境 + 底部右角木质棕微光 + 暖橙强调，工业设计作品集感 |
| `pink-script` | 夜间时装、香水广告、高级杂志 | DM Serif Display 衬线脚本（最大 600px）+ Inter 300 正文 + JetBrains Mono 目录标签，热紫红墨水 + 暗暖黑纸 + 电影颗粒，Maison 季刊 lookbook 感 |

---

## 转换器能力 / Converter Capabilities

`scripts/pptd2pptx.py` 基于 `python-pptx` 实现，支持：

| PPTD 元素 | PPTX 输出 | 备注 |
|-----------|-----------|------|
| `text` | 文本框 + 富文本 | 支持 HTML 子集、主题样式引用、对齐、自动换行 |
| `shape` | AutoShape | rect、roundRect、ellipse、triangle、star5、flowchart 等 |
| `image` | 图片 | 本地路径自动解析，支持裁剪与边框 |
| `table` | 表格 | 表头/数据行交替填充、边框、字体主题化 |
| `chart` | 真实图表 | 柱状图、折线图、饼图、条形图，支持 `seriesStyle`（`smooth`/`line`/`width`/`marker`） |
| `icon` | 占位标签 | 当前版本渲染为 `[iconName]`，待接入 Font Awesome / SVG |
| `background` | 幻灯片背景 | solid / gradient / image |
| `theme` | 主题色与字体 | 颜色引用 `$key`、文本样式 `$style` 自动解析 |
| `border` | 形状边框 | 线宽、线色 |
| `fill` | 形状填充 | solid / gradient |
| `rotation` | 旋转 | 以度为单位 |
| `shadow` | 形状阴影 | 统一接口：`offset`/`dx`/`dy`/`offsetX`/`offsetY` |
| `opacity` | 透明度 | 形状与文本 alpha 通道 |
| `gradient` | 渐变填充 | 多 stop 线性渐变（`gsLst`） |
| `freeform` | 自由路径 | SVG 路径命令：M/L/C/Q/Z/H/V，支持逗号分隔坐标 |
| `animation` | 动画效果 | fade/wipe/flyIn/peekIn/growShrink 等，支持 click/withPrevious/afterPrevious 触发 |
| `pageNumber` | 自动页码 | 全局配置，支持位置/格式/字体自定义 |

---

## 工作流参考 / Workflow Reference

| 阶段 | 负责方 | 关键文件 |
|------|--------|----------|
| 1. 读取输入 | 主 agent | `design.md`, `content.docx` |
| 2. 适配主题 | 主 agent | `references/design-adapter.md` |
| 3. 创建大纲 | 主 agent | `assets/outline-template.md` |
| 4. 创建主文件 | 主 agent | `<name>.pptd` |
| 5. 构建页面 | Subagent | `references/subagent-prompts.md` |
| 6. 检查修复 | Subagent / 主 agent | `scripts/check.sh` |
| 7. 导出 PPTX | 用户 / 转换器 | `scripts/pptd2pptx.py` |

---

## 许可证 / License

MIT
