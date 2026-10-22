# UI QA review - run3 pages

Reviewed every page at 360x780 (touch, mobile emulation) and 1440x900, scrolling each page from top to end and capturing viewport tiles plus full-page screenshots. Findings are limited to visible layout defects; colours, wording, image content and interaction behaviour are excluded.

## Findings per page

| Page | Findings |
| --- | --- |
| p01 | 0 |
| p02 | 0 |
| p03 | 1 |
| p04 | 0 |
| p05 | 0 |
| p06 | 0 |
| p07 | 1 |
| p08 | 0 |
| p09 | 2 |
| p10 | 1 |

## Detail

- p03, phone: in the Buttons demo the link button is 49.6px tall against 46.6px for the adjacent button and input, so the three controls do not share a baseline.
- p07, phone: the two hero pills wrap and overlap by about 18px; the Components pill covers the lower edge of the Utilities pill.
- p09, phone: the code blocks use content-box sizing with a 2em left padding, pushing the article to 455px wide in a 360px viewport. The page scrolls sideways and long code lines are cut at the right edge.
- p09, phone: the data table is compressed to 304px with 1px cell padding, so headers read `mpgcyl disp` and numbers run together as `1601103.902.62`.
- p10, phone: the fixed 32x32 menu button renders the 63px text label `listview`, which overflows the control and is clipped by the viewport edge.

## Checked and not reported

- p02, p03, p08, p10 code blocks that scroll horizontally inside their own `pre` elements; the page itself stays at viewport width.
- p04 and p06 tables that sit inside horizontally scrollable wrappers; the page does not scroll sideways and the clipped columns remain reachable.
- p06's fixed navigation and p10's off-canvas menu, which use intentional horizontal overflow.
- p01, p05 had no visible layout defects in either viewport.
