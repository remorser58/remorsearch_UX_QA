# Layout review

14 visible layout defects across 12 saved pages. Pages were reviewed individually in Chromium at 360x780 CSS px with touch emulation and at 1440x900 CSS px. Every page was scrolled from top to end; long-page screenshots were inspected in readable overlapping regions. The supplied Remorsearch UX QA skill and scan command were used.

| Page | Findings |
| --- | ---: |
| p01 | 1 |
| p02 | 1 |
| p03 | 1 |
| p04 | 2 |
| p05 | 0 |
| p06 | 3 |
| p07 | 0 |
| p08 | 1 |
| p09 | 1 |
| p10 | 1 |
| p11 | 1 |
| p12 | 2 |

The main issues are narrow-screen overflow in navigation and tables, mailbox text escaping its rows at both sizes, and compressed or incorrectly wrapped controls. All findings are P2 or P3. No visible defects were confirmed on p05 or p07.

Pages and assets were kept unchanged. Own scripts, screenshots, measurements and reports are contained in this output directory. Screenshot references in findings.json are relative to this directory; focused captures have adjacent receipts. Scan candidates were checked against pixels and false positives were dismissed in review-notes.md.

Scope: saved local pages and loaded local assets only. External HTTP(S) requests were blocked in the supplemental browser review. Colours, contrast, copy, images, demo data, accessibility conformance and interaction behaviour were excluded from findings. Safari, physical devices and unrequested interaction states were not reviewed. Proposed fixes were not applied or tested.
