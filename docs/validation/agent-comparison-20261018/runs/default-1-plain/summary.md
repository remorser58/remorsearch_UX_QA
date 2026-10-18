# UI QA summary

All eight pages were rendered with Playwright Chromium at the requested viewports (phones at 360x780 and 393x852, the dashboard at 1440x900) and scrolled from top to bottom. Text clipping, overlap, covered text, off-screen content, font size, contrast and sibling spacing were measured in the DOM, and every reported item was confirmed in the screenshots.

| Page | Findings |
| --- | --- |
| product1-a.html | 0 |
| product1-b.html | 7 |
| product2-a.html | 8 |
| product2-b.html | 0 |
| product3-a.html | 0 |
| product3-b.html | 7 |
| product4-a.html | 6 |
| product4-b.html | 0 |

Product1-b, product2-a, product3-b and product4-a contain all 28 findings. Their main problems are headings with line-height around 0.7 so lines overlap, fixed-width or nowrap boxes that cut off prices, labels, titles and addresses, content hidden under fixed headers or bottom bars, 10px body text, and one-off 3-6px margin or padding overrides that break alignment or rhythm. Product1-a, product2-b, product3-a and product4-b rendered cleanly at every checked size.

No text failed WCAG contrast in the checked states.

Expected or borderline behavior was not reported as a defect. This covers the screen-reader-only "필수 선택" label, the horizontally scrolling pairing carousel, the ellipsis on the long campaign name in the dashboard table (the full name appears in the detail panel), and the ellipsis on the pay-bar order summary. It also covers the 10px business-information footer in product4, which is identical in both versions. The pairing carousel in product1-a and product1-b has its first card flush with the screen edge (x=0) even though the row has 16px side padding. That looks like a shared design choice, but it may be worth a look.

