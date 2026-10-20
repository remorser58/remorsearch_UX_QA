# UI QA review: 4 saved pages

Scope: read-only rendered review of p01 (Materia docs), p02 (Grayscale), p03 (Lux docs), p04 (Light Bootstrap dashboard) at 360x780 with touch emulation and 1440x900. Every page was scrolled top to bottom at both sizes; the bundled ergonomics scan could not launch Chromium in this sandbox (driver exit 4, then no output), so I captured screenshots and geometry directly with Playwright 1.56.1 and Chromium headless shell using --single-process.

Findings: 6 total.

- p01 (2): the 420px-wide large pagination pushes the whole page to 433px at phone width, which drags the fixed navbar off screen (73px of sideways scroll, hamburger at x=365..421).
- p02 (0): no layout defects at either size. The mobile menu opens as a normal full-width list and all sections fit inside 360px.
- p03 (2): the 465px table overflows the 360px viewport to 480px and clips two columns; the 419px large pagination also runs past the right edge.
- p04 (2): at 360px the 260px sidebar stays in flow, leaving the dashboard a 100px-wide column with unreadable cards; the top bar also wraps into a tall stack.

Not tested: interaction states beyond opening the p02 mobile menu, hover/focus styling, and anything below the last captured tile on pages longer than the 30-tile cap.
