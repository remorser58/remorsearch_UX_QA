# Layout review

Read-only review completed for all ten saved pages at 360x780 CSS px with touch emulation and 1440x900 CSS px. Each page was scrolled from top to end; screenshots were viewed and suspected defects checked against DOM geometry.

Found 9 visible layout defects: 3 P2 and 6 P3. No P0 or P1 findings. Fix the p04 caption overlap, p07 hero-button overlap, and p09 document overflow first, then recheck the affected layouts.

| Page | Findings |
| --- | ---: |
| p01 | 0 |
| p02 | 0 |
| p03 | 0 |
| p04 | 1 |
| p05 | 1 |
| p06 | 2 |
| p07 | 3 |
| p08 | 0 |
| p09 | 1 |
| p10 | 1 |

The findings and concrete fixes are in [findings.json](findings.json). Evidence paths in each item are relative to this folder. The scan captures every page at both sizes in [scan/](scan/); closer screenshots have adjacent capture receipts, and [review-notes.md](review-notes.md) records coverage and dismissed candidates.

Only rendered layout was assessed. No page changes, form submissions, external browsing, or delegation occurred. Interaction behavior, accessibility, Figma fidelity, other viewport sizes, WebKit, and physical devices were outside this review. No fixes or post-fix replay were performed.
