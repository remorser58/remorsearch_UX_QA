# UI QA summary

Read-only review of eight local pages in Chromium (Playwright 1.56.1), following the Remorsearch UX QA persona-qa fast path. Phone pages were checked at 360x780 and 393x852, and the dashboard at 1440x900. Each page was scrolled from top to end, and the content under fixed bars was measured at scroll 0 and at maximum scroll. Every finding was confirmed in viewed screenshots and backed by DOM geometry and computed styles.

## Findings per page

| Page | Findings | Highest |
| --- | --- | --- |
| product1-a.html | 1 | P3 |
| product1-b.html | 8 | P1 |
| product2-a.html | 8 | P1 |
| product2-b.html | 0 | - |
| product3-a.html | 0 | - |
| product3-b.html | 7 | P1 |
| product4-a.html | 7 | P1 |
| product4-b.html | 1 | P3 |

Total: 32 (P1: 5, P2: 17, P3: 10).

## Most important problems

- product1-b: the fixed cart bar covers the last option ('일회용 수저·포크 받기') even at maximum scroll, so it cannot be seen or tapped.
- product2-a: the headline is cut at the right edge because of nowrap; the callout, a stat value and the last related card also hide text.
- product3-b: the fixed header covers the page title at the top of the page; tabs, a KPI note and the vacation badge clip or overlap text.
- product4-a: the fixed header hides the delivery date, and the delivery address, a price and the installment table are cut off before payment.

Two issues appear in both versions of a product. Both product1 pages snap the pairing carousel 16px on load, which puts the first card's label against the screen edge. Both product4 pages set the footer business information at 10px.

## Candidates dismissed after viewing pixels

- #pairing-row horizontal overflow (product1): this is an intended swipe carousel with a '옆으로 넘겨 보기' hint and dots. Only its edge alignment is reported.
- #sr-required-size (product1): visually hidden screen-reader text.
- #cell-campaign-3 (product3) and #paybar-summary (product4): deliberate one-line ellipsis. The full text appears in the side panel or the order list.
- Text under fixed bars at scroll 0 that scrolls clear before the end of the page: this is normal fixed-bar behavior.
- The contrast check found no text below 4.5:1.

## Limits

- The skill's bundled scan (scripts/ergo_qa.py scan) could not launch Chromium in this sandbox, even with REMORSEARCH_CHROMIUM_ARGS=--single-process. A direct Playwright launch with --single-process worked and was used for all captures, so the scan's crop artifacts are missing.
- Only Chromium emulation was used. Safari/WebKit, real devices, safe areas and screen readers were not tested.
- Only the default state was reviewed. Selecting options, quantity changes, coupon or payment interactions, and hover or focus states were not exercised.

