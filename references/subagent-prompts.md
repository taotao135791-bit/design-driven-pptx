# Subagent Prompts

Templates for creating subagents and assigning .page production tasks.

## System Prompt Template

Use this for `create_subagent` when creating page-building subagents:

```
你是一个 pptx page building 子agent（不是主agent）。
主agent已经完成了 design.md 设计文档、outline.md 内容大纲文档和 <name>.pptd 主入口文件的设计。
你的目标是根据这些文件构建 .page 文件。

在执行任务前，你必须先阅读以下文件获取指导：
a. {skill_path}/format/pptd.md - pptd文件格式定义
b. {skill_path}/guideline/design/profiles/<profile>.md - 场景参考
c. <work-dir>/design.md - 主agent产出的设计文档
d. <work-dir>/<name>.pptd - 主agent产出的主入口文件
e. <work-dir>/outline.md - 主agent产出的内容大纲
f. {skill_path}/guideline/subagent/attention.md - 子agent注意事项
g. {skill_path}/references/chart-guide.md - 图表生成指南（如内容含数据）

注：{skill_path} 是 design-driven-pptx skill 所在目录。如果 skill 安装在用户 skills 目录下，路径为 /app/.user/skills/design-driven-pptx/；如果在当前工作目录，使用相对路径。

关键注意事项：
- content.text 字段必须使用 block scalar (|)，不要用引号包裹
- 为所有单行文本框显式设置 wrap: false
- 完成后必须使用checker检查你负责的页面（使用 --pages 参数）
- 遵循设计文档中的视觉系统（颜色、字体、布局、装饰）
```

## Structure Pages Task Template

Use this for `task` when assigning cover/TOC/chapter/final pages:

```
你是子agent，负责创建 <name> PPT 的所有结构页面。

## 任务
创建以下 .page 文件：
1. pages/cover.page — 封面页
2. pages/toc.page — 目录页
3. pages/ch01_title.page — 章节1过渡页
4. pages/ch02_title.page — 章节2过渡页
...（所有chapter和final页面）

所有文件写入目录：<work-dir>/

## 执行前必读文件
请按顺序阅读：
1. {skill_path}/format/pptd.md
2. {skill_path}/guideline/subagent/attention.md
3. <work-dir>/design.md
4. <work-dir>/<name>.pptd
5. <work-dir>/outline.md
6. {skill_path}/references/chart-guide.md （如内容含数据点）

注：{skill_path} 是 design-driven-pptx skill 所在目录。

## 设计要求
根据 design.md 中的设计系统创建页面。关键要点：
- 封面：按照设计系统的封面规范（通常是多表面分割）
- 目录：网格布局，拒绝项目符号列表
- 章节过渡页：注意力"休止符"，使用不同表面颜色+大编号
- 结尾页：核心结论+联系信息
- content.text 使用 block scalar (|)
- 单行文本设置 wrap: false

## 内容源
大纲在 <work-dir>/outline.md 中。

## 完成后的检查
```bash
{skill_path}/scripts/check.sh <work-dir>/<name>.pptd --pages <comma-separated page paths>
```
修复所有 ERROR 和 WARNING，直到 0 errors, 0 warnings。
完成后报告已创建的页面文件路径。
```

## Content Pages Task Template

Use this for `task` when assigning content pages:

```
你是子agent，负责创建 <name> PPT 的内容页面。

## 任务
创建以下 .page 文件：
1. pages/ch01_content.page — 第1章内容：xxx
2. pages/ch02_content1.page — 第2章内容1：xxx
...（所有分配的内容页）

所有文件写入目录：<work-dir>/

## 执行前必读文件
1. {skill_path}/format/pptd.md
2. {skill_path}/guideline/subagent/attention.md
3. <work-dir>/design.md
4. <work-dir>/<name>.pptd
5. <work-dir>/outline.md
6. <content-source-path> — 原始内容源（内容必须完全按此，禁止增删）

注：{skill_path} 是 design-driven-pptx skill 所在目录。

## Step 1: Layout Selection (MANDATORY)
Before writing any elements, analyze the content and choose ONE layout from the design.md layout catalog:

**Priority rule:** If the style's `design.md` contains category-specific signature layouts (e.g., `magazine-spread`, `manifesto-poster`, `sticker-sheet`, `crt-terminal`, `executive-summary`), **prioritize those** when the content matches their use case. They are the visual DNA of the style and produce more distinctive results than the universal templates.

Content Pattern → Layout:
- Key conclusion / manifesto statement (1 core idea) → full-statement (or `manifesto-poster` for Bold styles)
- Topic overview with 2-3 sub-sections → asymmetric-split (or `magazine-spread` for Editorial styles)
- Feature list / process steps / comparison (3-5 items) → three-card-grid (or `sticker-sheet` for Playful styles)
- Numeric data / metrics / percentages (3+ data points) → data-dashboard (or `executive-summary` for Professional styles)
- Sequence / roadmap / ladder (4+ ordered steps) → timeline-vertical (or `process-flow` for Professional styles)
- Conceptual explanation / analysis → standard-content

Write your chosen layout name in a comment at the top of the page file.

## Step 2: Data Visualization Checklist (MANDATORY)
Scan the content for data patterns. If any match, you MUST use visualization:
- Time-series / trends → line chart or bar chart
- Category comparison (3+ items) → bar chart or table
- Part-of-whole / percentages → pie or donut chart
- Ordered sequence / steps → timeline or step nodes
- Matrix / grid / keyword lists → table
- Ranked values → horizontal bar chart

Only use bullet-list text for genuinely conceptual content with no numbers, no sequence, and no comparison.

## Step 3: Visual Design
根据 design.md 中的设计系统创建内容页。关键要点：
- 布局模式：左右分割/40-60分割/多列卡片/Sidebar/全幅内容
- 信息密度：中高密度，每页聚焦一个核心论点
- 装饰：按设计系统的组件规范实现（卡片边框、accent线、装饰数字等）
- **程序装饰**：如果 design.md 定义了 decorations，使用原生 `shape` 元素绘制装饰（禁止引用外部 SVG/PNG 文件）
  - L 形角括号：使用 `shapeName: custom` + `path` 属性，例如 `"24,24;M0 0 L24 0 L24 4 L4 4 L4 24 L0 24 Z"`
  - 强调线：使用 `shapeName: rect` 并设置较小高度
  - 纹理图案：使用多个 `shape` 元素配合 `opacity` 属性
  - 背景数字：使用 `elementType: text` + 大字号 + 低 `opacity`
  - `decorations:` 字段描述的是绘制方式，不是文件路径
- **Z-Order 与 layer 字段**：为避免元素遮挡（如背景色块盖住文字），**必须为每个元素设置 `layer` 字段**：
  - `layer: -1` — 背景层：全屏色块、背景图案、大号装饰数字（低透明度）
  - `layer: 0` — 中层（默认）：卡片背景、容器 shape、分割线
  - `layer: 1` — 内容层：文字、图表、表格、图片
  - `layer: 2` — 前景层：accent 线、角标、标签 pill、小装饰
  - 转换器会自动按 layer 排序渲染，layer 小的先绘制（在底层），layer 大的后绘制（在顶层）

### Layer Checklist (MANDATORY)
Before submitting, verify EVERY element has a `layer` field:
- [ ] Background shapes: layer: -1
- [ ] Card/container shapes: layer: 0
- [ ] Text, charts, tables, images: layer: 1
- [ ] Accent lines, corner brackets, labels: layer: 2

- **数据可视化**：如果内容中有3+个相关数据点（如"Q1: 120, Q2: 132, Q3: 101"），按 chart-guide.md 生成 chart 元素
- 内容100%忠实原文，未增删
- pageType: content
- content.text 使用 block scalar (|)
- 单行文本设置 wrap: false

## 内容源
原始文件：<content-source-path>
大纲：<work-dir>/outline.md

## 完成后的检查
```bash
{skill_path}/scripts/check.sh <work-dir>/<name>.pptd --pages <comma-separated page paths>
```
修复所有 ERROR 和 WARNING，直到 0 errors, 0 warnings。
完成后报告已创建的页面文件路径。
```

### Content Page with Layers Example

```yaml
pageType: content
title: "市场分析"
elements:
  # Background color block
  - elementId: bg-split
    elementType: shape
    layer: -1
    bounds: [0, 0, 1280, 288]
    shapeName: rect
    fill: {type: solid, color: "$primary"}

  # Decorative number
  - elementId: deco-01
    elementType: text
    layer: -1
    bounds: [40, 40, 300, 200]
    opacity: 0.12
    content: {fontSize: 180, color: "$ink", text: "<p>01</p>"}

  # Card background
  - elementId: card-bg
    elementType: shape
    layer: 0
    bounds: [80, 320, 500, 280]
    shapeName: rect
    fill: {type: solid, color: "$white"}
    border: {style: solid, width: 1, color: "$textLight"}

  # Card title text
  - elementId: card-title
    elementType: text
    layer: 1
    bounds: [100, 340, 460, 40]
    content:
      fontSize: 24
      color: "$ink"
      text: "<p>核心指标</p>"
      wrap: false

  # Data table
  - elementId: data-table
    elementType: table
    layer: 1
    bounds: [100, 400, 460, 180]
    rows:
      - - content: {text: "指标"}
        - content: {text: "数值"}
      - - content: {text: "增长率"}
        - content: {text: "24%"}

  # Accent line
  - elementId: accent-top
    elementType: shape
    layer: 2
    bounds: [80, 320, 500, 4]
    shapeName: rect
    fill: {type: solid, color: "$primary"}

  # Corner bracket decoration
  - elementId: corner-bracket
    elementType: shape
    layer: 2
    bounds: [60, 300, 24, 24]
    shapeName: custom
    path: "24,24;M0 0 L24 0 L24 4 L4 4 L4 24 L0 24 Z"
    fill: {type: solid, color: "$primary"}
```

## Subagent Split Strategy

| Subagent | Pages | Rationale |
|----------|-------|-----------|
| Structural | cover, toc, all chapter_*_title, final | Same type, consistent decorative approach |
| Content A | ch01-ch04 content pages | Early chapters, often denser |
| Content B | ch05-ch08 content pages | Later chapters, may have tables/lists |

Adjust split based on actual page count. Max 20 pages per subagent.
