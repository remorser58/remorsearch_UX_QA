Reviewed all ten saved pages in Chromium at 360×780 CSS px with touch enabled and 1440×900 CSS px. Scrolled each page from top to bottom and inspected viewport screenshots and DOM measurements. Pages were not modified; external requests were blocked.

Found 8 layout defects:

| Page | Findings |
| --- | ---: |
| p01 | 1 |
| p02 | 0 |
| p03 | 0 |
| p04 | 1 |
| p05 | 1 |
| p06 | 1 |
| p07 | 1 |
| p08 | 1 |
| p09 | 1 |
| p10 | 1 |

Five findings are P2 and three are P3. Findings include oversized images and fields, an overlapping figure caption, misaligned checkbox/radio labels, an alert control wrapping into the wrong row, code overflowing the page, and a clipped menu label.

Intentional internal scrolling in code blocks, tables and the p06 navigation was excluded. Missing images, colours, wording, demo data and interaction behaviour were excluded. Repeated instances of the same defect on a page are grouped into one finding. Evidence screenshots and measurement files are saved beside findings.json.
