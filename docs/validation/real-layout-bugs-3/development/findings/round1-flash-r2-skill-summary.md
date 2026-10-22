# UI layout QA

I reviewed all 12 saved pages at 360x780 with touch emulation and at 1440x900, scrolling each page from top to end. The review was read-only; no page files were changed.

Twelve visible layout defects are recorded in `findings.json`. The most consequential are the phone header overflow on p01, p02, p05, p08, and p12, the p04 phone header collision, the p09 and p11 tables that make the whole page scroll sideways, and the p12 inbox preview that spills past its row.

I dismissed the scanner's chart and fixed-layer occlusion candidates where the pixels showed normal paint order. I also dismissed the p07 logo offset, which was within the glyph's optical centering. p03, p06, and p07 had no visible layout defect.

Limits: the pages were opened as local files in Chromium only. Real devices, Safari/WebKit, hover states, and interactions were not tested. The long docs and table pages were captured in overlapping viewport screens covering their full heights.
