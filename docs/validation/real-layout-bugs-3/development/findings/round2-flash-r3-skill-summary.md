# UI QA summary

Reviewed p01-p04 at 360x780 with touch emulation and at 1440x900, scrolling each page from top to end. Three visible layout defects were confirmed; p04 had none.

- p01: phone layout keeps the desktop sidebar and 960px content canvas, so navigation paints over the article and 600px of the page is clipped.
- p02: phone card heading is truncated to "Top Campaign Perfor..." by a nowrap/ellipsis constraint.
- p03: phone profile cards place the rating strip over the second Address line in all nine cards.
- p04: no visible clipping, overlap, off-screen content, wrapping break, alignment or size mismatch at either viewport.

Candidates involving canvas hit areas, hidden accordion content, intentional submenu spacing and box-only sidebar overlap were dismissed after inspecting the rendered pixels.
