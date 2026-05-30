# Main Agent Workflow

The main agent personally completes steps 1-4. Subagents only handle step 5.

## Step 1: Read Inputs

Read both input files:
- `design.md` — Parse colors, typography, layout patterns, components, decorative elements
- Content source (docx/markdown) — Parse structure, chapters, key points

Also read the PPTD format spec: `{skill_path}/format/pptd.md`

## Step 2: Adapt Design → PPTD Theme

Read `references/design-adapter.md` for detailed mapping rules.

Produce a `design.md` file under `<work-dir>/` containing:
1. Profile baseline declaration (which profile matches)
2. Style baseline declaration
3. Style details (colors, fonts, containers, images)
4. Layout system (margins, special pages, content page patterns)
5. Style usage rules
6. Risk prohibitions
7. Theme YAML definition (the PPTD theme block)

The theme YAML is the critical output — it will be embedded directly into the .pptd file.

Canvas size: `[1280, 720]` for 16:9.

## Step 3: Create outline.md

Read `assets/outline-template.md` for the format.

Rules:
- **Content fidelity**: Strictly follow the source document. No additions, no deletions.
- **Page types**: cover, table_of_contents, chapter, content, final
- **Chapter consistency**: If using chapter transition pages, ALL chapters must have one
- **TOC consistency**: If using TOC, chapter list must match chapter page titles
- **Page count**: Typically 15-25 pages for a standard deck

For each content page, write:
- Title
- Content description (reference source paragraph, summarize core message in 1-2 sentences)
- Sources (if applicable)

## Step 4: Create .pptd Master File

Produce `<work-dir>/<name>.pptd` containing:
1. `title`: Presentation title
2. `size`: [1280, 720]
3. `theme`: The complete theme YAML from step 2
4. `pages`: Ordered list of .page file paths (e.g., `pages/cover.page`)

The `pages` list is the contract with subagents — every .page referenced must be created.

## Step 5: Dispatch Subagents (Parallel)

Read `references/subagent-prompts.md` for detailed templates.

### Strategy

- **1 structural subagent**: Cover + TOC + all chapter transitions + final page
- **2-3 content subagents**: Split content pages among them (similar pages to same agent)
- Max 20 pages per subagent

### Subagent Creation

Use `create_subagent` with a system prompt that declares:
- Identity: pptx page building subagent (not main agent)
- Main agent has completed design.md, outline.md, and .pptd
- Goal: build assigned .page files
- Must-read files before execution

### Task Assignment

Use `task` with prompts containing:
- Which pages to create (file names from the .pptd pages list)
- Content writing mode: summary writing (content source provided)
- Output directory path
- Paths to all reference files

### Parallel Dispatch

Launch all subagent tasks in a single turn. They are independent and can run in parallel.

## Step 6: Check & Fix

After all subagents complete:

```bash
{skill_path}/scripts/check.sh <work-dir>/<name>.pptd
```

If `{skill_path}` is the skill's own directory, use `./scripts/check.sh`. If the skill is installed to the system's skills path, use the absolute path.

Run **without** `--pages` for full check.

Fix rules:
1. Fix ALL ERRORs first (cause conversion failure)
2. Fix ALL WARNINGs unless clearly intentional design (e.g., decorative low-opacity elements)
3. Fix in parallel (multiple edit_file calls in one turn)
4. Re-run checker after fixes until 0 errors, 0 unexpected warnings

## Step 7: Deliver

Build the artifact reference against the original .pptd path. Do NOT move the file alone — it depends on sibling `pages/` directory.

Inform the user:
- Page count and structure summary
- Checker result (0 errors, N warnings + explanations)
- How to preview and export to .pptx
