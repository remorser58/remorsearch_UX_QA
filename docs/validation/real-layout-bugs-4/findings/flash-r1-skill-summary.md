# Layout review — 8 saved pages (360x780 phone, 1440x900 laptop)

Read-only review. Every page was opened from its local file, scrolled to the end at both viewports, and checked against full-page and viewport screenshots plus DOM measurements (element rects, scrollWidth/clientWidth, overflow). Findings only cover visible layout problems; colour, wording, images and interaction were out of scope.

## Findings per page

| Page | Findings |
| --- | --- |
| p01 | 1 — comparison table clipped at the phone width (last column cut) |
| p02 | 1 — floated aside shrinks to 77px and breaks words mid-word |
| p03 | 0 — nothing beyond a 6px sideways scroll from one inline `code` label |
| p04 | 2 — table runs past both screen edges and scrolls the page sideways; textarea overflows its card |
| p05 | 1 — `col-sm-121` typo makes the content card 2288px wide at both viewports |
| p06 | 1 — fixed 610px install snippet makes the phone page scroll 250px sideways |
| p07 | 1 — fixed nav is 53px tall but its menu wraps to 78px and overlaps the page content |
| p08 | 1 — same aside defect as p02 (identical saved page) |

Total: 8 findings (2 P1 on p04/p05, 1 P1 on p06, 5 P2).

## Measurements worth keeping

- p04: document scrollWidth 401 at a 360px viewport; table 417px wide at x=-29..389; textarea 364px wide at x=38..401 inside a card ending at 348.
- p05: `.col-sm-121` card 2288px wide inside a 352px row; scrollWidth 2293 (phone) and 2534 (laptop).
- p06: `pre.npm` 610px wide with margin-right:-250px; scrollWidth 610.
- p07: nav height 53px, scrollHeight 78px; GitHub/Documentation buttons at y=36..72 while page content starts at y=80.

## Dismissed candidates

- p01/p02 tables: wide tables sit in their own `overflow:auto` boxes and do not move the page; treated as scrollable content, so only p01's cut header is reported.
- p03/p07 Picnic tab rows (`scrollWidth` 1567/2194): intentional 300%/400% carousel rows clipped by `overflow:hidden`.
- p03/p07 inline `code` reaching x=366: 6px of sideways scroll, too small to change reading and present in both copies of the page.
- p05 sticky header (scrollHeight 52 vs 53px height): 4px, no visible text cut.
- p06 laptop tab card clipping: intended one-tab-at-a-time carousel.

## Limits

Chromium headless only (no Safari/WebKit, no real device, no touch-gesture behaviour). Screenshots are in `cap3/` and `targeted/`, `targeted2/`; raw measurements in `cap3/report.json`.
