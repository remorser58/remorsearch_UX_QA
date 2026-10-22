# Layout review

Reviewed all ten listed local pages in Chromium at phone 360×780 CSS px with touch emulation and laptop 1440×900. Scrolled each page from top to end and inspected screenshots and DOM bounds. Page files were left unchanged.

Found 7 visible layout defects across five pages.

| Page | Findings |
| --- | ---: |
| p01 | 1 |
| p02 | 0 |
| p03 | 0 |
| p04 | 0 |
| p05 | 0 |
| p06 | 1 |
| p07 | 3 |
| p08 | 1 |
| p09 | 0 |
| p10 | 1 |

p01 has oversized images on phone. p06 has checkbox and radio alignment defects at both sizes. p07 has overlapping hero buttons, a split navigation item, and a displaced alert close glyph on phone. p08 has oversized full-width form controls at both sizes. p10 has a menu label extending beyond the phone screen.

No reportable visible layout defects were found on p02, p03, p04, p05, or p09. Expected internal scrolling in code blocks, tables, and navigation was excluded. Full-page capture artifacts were checked against viewport screenshots.

Details and fixes are in findings.json. Evidence screenshots are named in each finding; focus.json contains the corresponding DOM measurements.
