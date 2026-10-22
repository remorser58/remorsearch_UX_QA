# Rendered layout review

Found 13 visible layout defects. p01 had no confirmed defects at either requested size.

| Page | Findings | Affected viewport |
| --- | ---: | --- |
| p01 | 0 | none |
| p02 | 2 | phone |
| p03 | 2 | phone |
| p04 | 2 | phone |
| p05 | 1 | both |
| p06 | 1 | phone |
| p07 | 3 | phone |
| p08 | 2 | phone |

Reviewed all eight supplied local HTML pages independently in Chromium, at phone 360x780 with touch/mobile emulation and laptop 1440x900. Every page was scrolled from top to end. The supplied Remorsearch scan was supplemented with overlapping screenshots through the full document; touch panning also covered the visual-viewport tail on pages whose horizontal overflow enlarged the mobile layout viewport.

Priorities: contain the oversized Basic progress bar card on p05; restore phone navigation containment on p07; fix phone table, field and grid widths. Detailed selectors, measurements, screenshot paths and concrete fixes are in findings.json.

Evidence is under captures/, details/, pan-p05/ and pan-p06/. coverage.json records scroll positions; measurements.json and final-measurements.json record DOM geometry. The scan output is under scan/. Source HTML and page assets were not modified. All HTTP(S) requests were blocked; no external sites were opened.

Dismissed scan candidates: wrapped inline descriptions on p01 and paragraph boxes beside floats on p02/p08 do not visibly overlap. The very narrow aside itself is a confirmed wrapping defect. Tables and code samples with their own working overflow areas were not reported as clipping. The p05 logo is visibly intact, and its small padding differences do not establish misalignment. Checks at 320 px, contrast, accessibility semantics, missing images and interaction behavior were excluded from this report.

Limits: Chromium emulation only; no Safari, Firefox or physical-device verification. Only the saved default rendered pages and scrolling were reviewed. No fixes were applied or replayed.
