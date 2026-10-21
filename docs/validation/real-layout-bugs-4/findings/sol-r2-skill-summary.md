# Layout review

15 confirmed layout defects. All eight pages were reviewed independently at 360x780 with touch emulation and at 1440x900, scrolling from top to end. Pages were not modified.

| Page | Findings | Affected viewport |
| --- | ---: | --- |
| p01 | 0 | None |
| p02 | 2 | Phone |
| p03 | 4 | Phone and laptop |
| p04 | 1 | Phone |
| p05 | 0 | None |
| p06 | 1 | Phone |
| p07 | 4 | Phone and laptop |
| p08 | 3 | Phone |

Priorities: repair phone overflow and header containment; stack narrow sidebars/forms; reserve space for select arrows.

Evidence: `findings.json` links the viewed screenshots under `evidence/`; `measurements.json`, `target-measurements.json`, `detail.json`, and `selects.json` contain supporting geometry. `capture-index.json` and `ends/measurements.json` record full scroll coverage. The skill scan is retained under `scan/`. Its skipped middle intervals were covered by additional overlapping captures.

Dismissed scan candidates: wrapped inline text does not overlap its neighbouring code; paragraphs wrap around floated asides without covered glyphs; the inline quotation uses normal hanging punctuation; p01 tables and p05 code blocks scroll inside bounded containers; the p05 logo is fully painted; the p03 tooltip covering a neighbour is its intentional hover demonstration. Zero spacing between p08 navigation links was excluded as a spacing-only observation.

Scope: visible layout only, Chromium emulation. No external websites, interactions beyond scrolling, page edits, or delegated review. Safari/WebKit, physical devices, and unrequested interaction states were not tested.
