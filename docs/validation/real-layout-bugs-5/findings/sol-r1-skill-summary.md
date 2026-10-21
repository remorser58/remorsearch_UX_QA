# Rendered layout review

Reviewed all ten supplied local pages in Chromium at 360x780 with touch emulation and 1440x900. Scrolled each page from top to end and visually inspected the overlapping viewport captures. Pages were not modified; external network requests were blocked. Used the supplied Remorsearch UX QA scan, then confirmed findings against screenshots and DOM measurements.

Found 9 layout defects, grouping repeated instances with the same cause. No P0 or P1 findings.

| Page | Findings |
| --- | ---: |
| p01 | 1 |
| p02 | 0 |
| p03 | 0 |
| p04 | 0 |
| p05 | 1 |
| p06 | 1 |
| p07 | 3 |
| p08 | 1 |
| p09 | 1 |
| p10 | 1 |

The main defects are oversized images on p01, selection-control alignment on p05/p06, overlapping or split components on p07, overflowing form fields on p08, slight outer code-block overflow on p09, and a clipped phone menu label on p10. No visible in-scope defects were confirmed on p02, p03 or p04.

`findings.json` contains selectors, viewport scope, severity, measurements, evidence paths and proposed fixes. Original captures and their receipts are under `scan/*/runs/`; viewed contact sheets are under `unique-sheets/`. Direct confirmation screenshots and measurements are at this directory's root.

Dismissed scan candidates: p02's LaTeX/link overlap (readable pixels); p04/p09's inline h2 spacing (ordinary prose, not a list); p06's aside overlap (text wraps clear of the aside), quotation indent and brand offset (different element roles); p10's covered Features menu links (closed menu behind the page). Contained horizontal scrolling in code/table examples, normal viewport cutoffs, missing images and interaction behavior were excluded. Adaptation-probe findings outside the two requested sizes were excluded.

The scanner's remaining-coverage warnings on p01, p08 and p09 come from mobile layout/visual viewport differences after horizontal overflow. Their end captures were inspected, including the final license text, final horizontal rule and final paragraph, respectively. Repeated captures at an unchanged scroll position were viewed once.

Scope limits: saved default page states and Chromium emulation only; no Safari, real-device, task-flow or accessibility audit. Read-only authority covered the supplied pages and assets; all reviewer-created files stayed inside this output directory.
