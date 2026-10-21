Reviewed all eight saved pages in Chromium at 360×780 CSS px with touch/mobile emulation and 1440×900 CSS px. Each page was scrolled from top to end, and the captured screenshots were viewed. Two visible layout defects were confirmed.

| Page | Findings | Affected viewport |
| --- | ---: | --- |
| p01 | 0 | — |
| p02 | 0 | — |
| p03 | 1 | Laptop |
| p04 | 0 | — |
| p05 | 0 | — |
| p06 | 0 | — |
| p07 | 0 | — |
| p08 | 1 | Phone |

On p03, the social links sit at the left edge below the laptop hero in a separate 900px-high area. On p08, the introductory code panels extend 47px beyond the phone screen.

Findings and concrete fixes are in [findings.json](findings.json). Screenshots and measurements are retained in `scan/`, `captures/`, the `measure-*` folders, and `inspection.json`. The supplementary p01 laptop captures cover the scan's final scroll gap; p07 fits entirely within each viewport, so attempted scrolling remains at zero.

This was a read-only layout review. The page files were not modified. External requests were blocked. Missing images, unavailable embedded content, colours, wording, demo data, accessibility and interaction behaviour were excluded. The results apply to these saved pages in Chromium; Figma fidelity, other engines and physical devices were not assessed.
