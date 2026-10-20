# UI QA summary

Reviewed four saved pages at 360x780 touch emulation and 1440x900, scrolling each page from top to end. Screenshots and DOM measurements are retained under `scan/` and `scan-full/`.

| Page | Findings | Main issue |
| --- | ---: | --- |
| p01 | 1 | Large pagination row overflows the phone viewport by 72px. |
| p02 | 1 | Hero scroll-button icon sits about 3px below the control center. |
| p03 | 3 | Table and large pagination overflow the phone viewport; the hover code button covers a button label and text at laptop width. |
| p04 | 1 | Sidebar leaves only 100px for the dashboard on phone, collapsing cards and text. |

Dismissed candidates: the p01 checkbox group ends at x=354 inside a 360px screen; the p04 globe icon offset measured only the icon while the adjacent caret is part of the same control; p04 tables scroll inside their intended `.table-responsive` wrapper; p03 fixed-navbar cutoffs while scrolling are normal viewport clipping, not lost content.
