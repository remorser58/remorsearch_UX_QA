# UI QA review, 12 saved pages

Scope: read-only review of the listed local pages at 360x780 (touch) and 1440x900, scrolled top to end. Screenshots and DOM geometry were captured with Playwright 1.56.1 Chromium; the bundled scan could not launch a browser under the sandbox (exit 3), so each page was captured with a direct Chromium run using --single-process.

## Findings by page

| Page | Findings | Summary |
| --- | --- | --- |
| p01 | 0 | Dashboard renders cleanly at both sizes; the off-canvas chat contacts panel is clipped by its own container by design. |
| p02 | 1 | Phone page is 4 px wider than the screen because the header nav ends at x=364. |
| p03 | 1 | Phone page loads with the 250 px sidebar open over the content, covering two thirds of the screen. |
| p04 | 1 | Phone header cluster ends at x=380 and is clipped at 360; the avatar loses its right edge. |
| p05 | 0 | Clean at both sizes. |
| p06 | 2 | Laptop: first nav label renders as "ome" under the sidebar, and the footer copyright starts under the sidebar. |
| p07 | 0 | Clean; the off-screen icon belongs to the closed sidebar and is not visible. |
| p08 | 1 | Phone page is 412 px wide; the user avatar sits entirely outside the 360 px viewport. |
| p09 | 1 | Phone pagination is 344 px wide in a 304 px wrapper; the Previous button is cut 33 px at the left edge. |
| p10 | 0 | Clean at both sizes. |
| p11 | 0 | The wide tables and code blocks scroll inside their own containers, as intended; no page overflow. |
| p12 | 1 | Mailbox rows do not shrink: phone page scrolls to 940 px and laptop rows overflow the card and viewport, hiding the time column. |

## Coverage and limits

All 12 pages were captured at both sizes and scrolled to the end (24 page/device pairs). Judgements use the captured pixels plus element boxes; the review did not exercise menus, drawers or dropdowns, so defects visible only in those states are untested. Chromium emulation leaves Safari/WebKit, real touch devices and safe areas untested. No files outside the review folder were modified.
