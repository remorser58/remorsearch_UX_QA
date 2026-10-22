# Rendered layout review

Reviewed all eight supplied local pages in Chromium at 360x780 with mobile/touch emulation and at 1440x900. Scrolled every page from top to end; used touch scrolling to reach the phone visual viewport's end on p04. No page files were modified, and no websites were opened.

Three findings: p03 has detached social controls at both sizes; p04 has severe horizontal overflow on phone; p05 keeps narrow columns on phone, causing excessive wrapping and text overflow.

| Page | Findings | Severity |
| --- | ---: | --- |
| p01 | 0 | — |
| p02 | 0 | — |
| p03 | 1 | P2 |
| p04 | 1 | P1 |
| p05 | 1 | P2 |
| p06 | 0 | — |
| p07 | 0 | — |
| p08 | 0 | — |

The wide code/table examples on p01, p02 and p06 are contained scroll regions; they were not counted as page overflow defects. No other visible defects within the requested categories were found. Missing media and interaction behavior were excluded.

See findings.json for selectors, measurements and proposed fixes. Each finding names its supporting screenshots. The screenshot sequences and contact sheets also document the complete scroll review.
