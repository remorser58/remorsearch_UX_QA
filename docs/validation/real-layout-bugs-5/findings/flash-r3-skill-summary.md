# Rendered layout review — run3 pages p01-p10

Scope: 10 saved pages opened from file://, each at 360x780 CSS px with touch emulation and at 1440x900, scrolled from top to end. Read-only; no page files were changed. Measurements come from DOM geometry and from the full-page and viewport screenshots I inspected.

Result: 5 findings on 4 pages. p01, p02, p03, p05, p06 and p08 showed no layout defect I could confirm in the pixels.

| Page | Findings |
| --- | --- |
| p01 | 0 |
| p02 | 0 |
| p03 | 0 |
| p04 | 1 (clipped table on phone) |
| p05 | 0 |
| p06 | 0 |
| p07 | 2 (overlapping hero pills, uneven link wrap) |
| p08 | 0 |
| p09 | 1 (sideways page scroll on phone) |
| p10 | 1 (menu control label spills out of its box) |

Notes on things I checked and dismissed:

- Horizontal scrolling inside code blocks and wide tables is a deliberate overflow container on p02, p03, p04 (code) and p06, p08, so I only reported p04's table, where the 55% wrapper clips the table's own last column mid-word, and p09, where the code block widens the whole document instead of scrolling inside itself.
- p06's floated aside on laptop sits beside the paragraph with no text collision; the geometric overlap of the two boxes is whitespace, not visible occlusion.
- p03 and p08 grid examples collapse to one column per row on phone; that is the framework's documented mobile behaviour.
- Long empty stretches in the stitched full-page captures (p02, p04) are screenshot stitching artifacts; viewport captures at those offsets show painted content.

Evidence files: `findings.json`, `shots/*-full.png`, `crops/`.
