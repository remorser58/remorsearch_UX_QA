# UI review summary

Reviewed all eight saved pages at 360x780 (touch) and 1440x900, scrolling each to the end. Six layout defects were confirmed by screenshot and DOM measurement.

| Page | Findings | What is visible |
| --- | --- | --- |
| p01 | 0 | No layout defect found at either size. |
| p02 | 0 | Tables and long code blocks scroll inside their own boxes; nothing is clipped from the page. |
| p03 | 2 (phone) | The Contents sidebar collapses to 65px and overlaps the article heading. A long URL plus the fixed nav widen the document to 413px, so the page pans 53px sideways. |
| p04 | 1 (phone) | The comparison table is 417px wide in a 328px section and is centered past both edges, clipping the first-column labels. |
| p05 | 1 (both) | The typo class `col-sm-121` gives the main content wrapper a 2288px width; the page is 2534px wide on laptop and 2292px on phone, with text cut at the right edge. |
| p06 | 0 | The hero code strip is a horizontally scrollable `pre`; tabs show only the active card by design. |
| p07 | 1 (phone) | The fixed nav is 366px wide in a 360px viewport, producing a 6px sideways scroll. |
| p08 | 1 (phone) | Header nav links have no horizontal margin, so labels and underlines merge into one string. |

Screenshots and contact sheets are in `shots/`; raw geometry data is in `metrics.json`. The review was read-only.
