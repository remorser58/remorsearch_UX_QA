UI layout review of the eight saved pages.

Each page was opened from its local HTML file in Chromium (Playwright 1.56.1) at 360x780 with touch enabled and at 1440x900. Every document was scrolled from top to bottom in viewport steps before capture, and full-page screenshots plus element rectangles, scrollWidth/clientWidth and overflow values were collected. Suspect areas were re-checked with targeted DOM probes and zoomed crops.

Findings: 9 total.

| Page | Findings |
| --- | --- |
| p01 | 1 |
| p02 | 0 |
| p03 | 2 |
| p04 | 1 |
| p05 | 0 |
| p06 | 1 |
| p07 | 3 |
| p08 | 1 |

The clearest breakages are on p03 (the squeezed sidebar paints its 'Contents' heading and links over the article title and intro at phone width), p06 (the 610px hero snippet makes the whole phone page 250px wider than the viewport and pushes the nav menu off-screen), p04 (the comparison table overflows both sides of its 328px column and loses its row labels), p08 (the floated aside collapses to a 77px column and breaks words into single letters), and p07 (a transparent fixed 'Up you go' link is painted over code text at both widths).

Reported as lower-severity: p03's 53px sideways scroll from an unbreakable URL, p07's 6px grid overflow from the 'twelve' code chip and the nav border crossing the wrapped GitHub label, and p01's clipped third comparison column.

Not reported: hidden tab panels and horizontally scrollable code blocks (intentional overflow), the 'Overflowing table' demos on p02/p08 (labelled as intentional), tooltips shown over neighbouring buttons, and colour, wording or interaction issues.

Limitations: p05 produced no confirmed layout defect; its narrow justified footer and the 4px logo overflow inside the 48px sticky header were inspected but did not show visible clipping. Measurements were taken at a single load state per page, so hover-only and animation-only states were not reviewed.
