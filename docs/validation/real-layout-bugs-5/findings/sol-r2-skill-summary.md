# Layout review

Eight visible layout defects were confirmed: four P2 and four P3. No pages were modified.

All ten pages were reviewed from top to end in Chromium at 360x780 CSS px with touch emulation and 1440x900 CSS px. Screenshots were visually inspected; reported geometry was checked in the DOM.

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

Findings and concrete fixes are in `findings.json`. Confirmation screenshots and measurements are in `confirm/`; the complete scroll captures are in `captures/`.

The findings concern overflowing images, overlapping figure captions, checkbox/radio alignment, a displaced alert close control, oversized form fields, overflowing code, and clipped menu-control text.

Scrollable code/table contents and p06's horizontally scrollable navigation were not counted as lost content. Scanner candidates involving text wrapping around a float, inline-code spacing, and p10's concealed menu did not show visible defects.

Scope was limited to rendered layout at the two requested sizes. Interaction behavior, visual styling, missing assets, other browser engines, and real devices were outside this review. External network requests were blocked.
