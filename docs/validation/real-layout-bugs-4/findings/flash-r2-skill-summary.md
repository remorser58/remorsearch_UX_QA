# UI QA summary — run2 pages (p01–p08)

Read-only visual review of the eight saved pages at 360x780 (touch) and 1440x900. Every page was scrolled from top to end in viewport steps (5–50 captures per page) and each layout candidate from the ergonomics scan was opened as a crop or re-captured before it was accepted.

Findings: 9 total. p01 1, p02 0, p03 2, p04 1, p05 0, p06 1, p07 3, p08 1.

Most serious: p06 at phone width lays out at 610px, so the hero code line is cut and the fixed menu button sits 164px off-screen; p03 squeezes its Contents sidebar to 65px so the heading and links print over the article.

Dismissed after checking pixels and geometry: p01/p02 docs "small text overlaps code" (the text runs 6px past the code chip, no overlap); p02 laptop aside paragraph (box overlaps the aside, painted text does not); p03 tooltip crop (a tooltip over neighbouring buttons is expected overlay behaviour); p03/p06/p07 code blocks with internal horizontal scroll (contained, page does not pan); p02/p08 "Overflowing table" demos (intentional scrolling examples); p05 sticky header 4px vertical overflow (logo fully visible).

Coverage limits: Chromium only (no Safari/WebKit), synthetic viewports without device safe areas, no hover, focus, open menu or error states exercised; the p07 "Up you go" overlay was confirmed at rest positions while scrolling, not in every possible scroll offset.

