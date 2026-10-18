# UI QA summary

Verdict: product1-b, product2-a, product3-b and product4-a each have several defects users will notice. Four are P1: hidden or cut content on the main task. product1-a has one minor alignment defect. product2-b, product3-a and product4-b showed no confirmed defects.

| Page | Findings | P1 | P2 | P3 |
| --- | --- | --- | --- | --- |
| product1-a.html | 1 | 0 | 0 | 1 |
| product1-b.html | 8 | 1 | 5 | 2 |
| product2-a.html | 8 | 1 | 5 | 2 |
| product2-b.html | 0 | 0 | 0 | 0 |
| product3-a.html | 0 | 0 | 0 | 0 |
| product3-b.html | 7 | 0 | 5 | 2 |
| product4-a.html | 6 | 2 | 3 | 1 |
| product4-b.html | 0 | 0 | 0 | 0 |

Total: 30 findings, all in `findings.json`.

## Top actions

1. Reserve space for the fixed bars. Add bottom padding on product1-b and product2-a so the last option or card clears the bottom bar. Add top padding on product4-a and product3-b so the delivery date and the page title clear the header.
2. Let long text wrap. Remove the `nowrap`, fixed widths and `overflow:hidden` behind the cut article title (2-a), address and price (4-a), sauce chip (1-b), stat value (2-a), KPI note and tab (3-b).
3. Restore normal line heights (about 1.3-1.4) on the overlapping headings (1-b, 2-a, 3-b). Raise the 10px body/notice text to 14-16px (1-b, 2-a, 4-a).

## How the pages were checked

- Builds: the local files as given, identified by SHA-256 prefix: 1-a 8c2dda34a145, 1-b 855658c62433, 2-a 626a434828fe, 2-b 4301e40efe2b, 3-a 3621fda84ad6, 3-b a804b5311b5e, 4-a f1cd500bf61f, 4-b 77d17f1769a2.
- I ran the skill's scan (`ergo_qa.py scan`) on every page from top to end: phones on galaxy-s24 (360x780) and iphone-15 (393x852), the dashboard on laptop-1440 (1440x900). Chromium needed `--single-process` in this sandbox. Scan output is in `scan2/`.
- I viewed the top, middle and end screenshots for every page and device class. Each finding is confirmed in pixels and backed by DOM measurements (bounding boxes, scrollWidth/clientWidth, computed font size and line height) taken at both phone widths, or at 1440x900 for the dashboard.
- P1 second pass: I re-checked the four P1s (1-b #addon-cutlery, 2-a #cs-title, 4-a #eta-box, 4-a #addr-box-line) against their screenshots and measurements, and all four held. This was a labelled self-pass; no independent reviewer was used.

## Scan candidates dismissed

- #cell-campaign-3 ellipsis (3-a and 3-b): an intended single-line table cell. The full campaign name is shown in the '선택한 캠페인' panel.
- #paybar-summary ellipsis (4-a and 4-b): an intended one-line order summary above the pay button.
- Bell icon without tooltip (3-a and 3-b): it has the accessible name '알림 3개', and the issue is not visible in the rendered UI.
- CG-03 response time on 1-a: the page is static. The 2.2 s delay came from the scan driver running in single-process mode, not from the page.

## Observed but not reported

- The legal business footer (#biz-info) is 10px on both 4-a and 4-b. It is small, but it follows the usual fine-print convention for that block.
- Korean body text on product2 (both versions) breaks mid-word in places, for example '감/소' in a stat label and '보/드를' in the summary, because body copy lacks `word-break:keep-all`. Adding it would improve readability.

## Not tested

Chromium emulation only: Safari/WebKit, real devices, safe-area insets, OS text scaling and screen readers were not covered. Interactions (option selection, quantity, tabs, payment) were not exercised; the review covers the rendered default state at each scroll position.

