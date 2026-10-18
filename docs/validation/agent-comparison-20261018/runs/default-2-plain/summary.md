# UI QA summary

Pages were rendered in Playwright Chromium at 360x780 and 393x852 (phone) and 1440x900 (dashboard), scrolled top to bottom, and checked with screenshots plus DOM measurement (overflow and clipping, off-screen boxes, text overlaps, fixed bars at the start and end of scroll, line-height, font size, sibling spacing and alignment, contrast).

| Page | Findings | P1 | P2 | P3 |
|---|---|---|---|---|
| product1-a.html | 1 | 0 | 0 | 1 |
| product1-b.html | 8 | 3 | 3 | 2 |
| product2-a.html | 8 | 3 | 3 | 2 |
| product2-b.html | 0 | 0 | 0 | 0 |
| product3-a.html | 0 | 0 | 0 | 0 |
| product3-b.html | 6 | 1 | 4 | 1 |
| product4-a.html | 6 | 3 | 2 | 1 |
| product4-b.html | 0 | 0 | 0 | 0 |

Most serious problems: in product1-b, the size option name is covered by the BEST ribbon and the last option sits under the cart bar. In product2-a, the headline runs off screen, the summary is covered by the callout, and the last related case sits under the CTA bar. In product3-b, the page title is under the fixed header. In product4-a, the ETA banner is under the header, and the address, item price and installment totals are clipped.

product2-b, product3-a and product4-b showed no defects. The carousel inset issue (#pairing-row) appears identically in product1-a and product1-b.

Checked and not reported because they behave as intended: the visually hidden screen-reader text (#sr-required-size), cards beyond the edge inside the horizontal carousel, ellipsis truncation in the pay-bar summary (#paybar-summary) and the long campaign name cell (#cell-campaign-3, full name shown in the side panel), and the tight line-height on single-line KPI numbers. The 10px business-info footer (#biz-info) is identical in product4-a and product4-b. It is small but conventional legal fine print, so it was left out of the findings. No text failed WCAG AA contrast.

