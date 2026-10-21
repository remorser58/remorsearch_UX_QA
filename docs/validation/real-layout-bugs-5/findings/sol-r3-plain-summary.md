# UI layout review

Reviewed all ten local pages at 360 × 780 CSS px with touch emulation and at 1440 × 900 CSS px. Scrolled each page from top to end and inspected overlapping viewport screenshots and DOM measurements. The source pages were unchanged; no websites were opened.

Found 8 defects: 7 P2 and 1 P3.

| Page | Findings |
| --- | ---: |
| p01 | 0 |
| p02 | 0 |
| p03 | 0 |
| p04 | 2 |
| p05 | 0 |
| p06 | 2 |
| p07 | 2 |
| p08 | 0 |
| p09 | 1 |
| p10 | 1 |

The findings cover a figure-caption overlap and clipped table caption on p04, control and navigation alignment on p06, overlapping hero buttons and a displaced alert close glyph on p07, page overflow on p09, and a clipped menu control on p10.

Dedicated horizontal table/code/navigation scrolling, missing images, and non-layout issues were excluded. Full findings and fixes are in findings.json. Screenshot filenames in each finding refer to files in this directory.
