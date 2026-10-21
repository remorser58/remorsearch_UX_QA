# Layout review

Reviewed all eight local pages independently in Chromium at 360×780 CSS px with mobile/touch emulation and at 1440×900 CSS px. Scrolled each page from top to bottom and inspected screenshots and DOM geometry. Touch scrolling was also used to reach the visual bottom of pages whose overflow enlarged the mobile layout viewport. Pages were not modified.

| Page | Findings |
|---|---:|
| p01 | 0 |
| p02 | 2 |
| p03 | 3 |
| p04 | 2 |
| p05 | 1 |
| p06 | 0 |
| p07 | 1 |
| p08 | 3 |
| Total | 12 |

One P1 finding affects the progress page at both sizes. The remaining findings affect phone layouts: overlapping headings and reference labels, an off-screen menu control and table, oversized form/media elements, a severely squeezed aside, and joined navigation labels. No reportable defects were found on p01 or p06.

Contained horizontal scrolling in code/table examples and hidden tab slides were excluded. Colours, contrast, wording, image content, missing images, demo data and interaction behaviour were excluded. Repeated instances of the same defect within a page are grouped.

The JSON contains selectors, measured evidence and proposed fixes. Screenshots and supporting geometry are saved beside it; fixes were not applied.
