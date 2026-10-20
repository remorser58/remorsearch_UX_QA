# Rendered layout review

Reviewed all four local pages in Chromium at 360 × 780 CSS px with mobile/touch emulation and at 1440 × 900 CSS px. Scrolled each page from top to its maximum scroll position, including the dashboard's separate main-panel scroller, and inspected screenshots throughout. Reviewed the long pages' footer regions in full-page captures as well. External network requests were blocked; the source pages were not modified.

| Page | Findings | Affected viewport |
| --- | ---: | --- |
| p01 | 1 | Phone |
| p02 | 0 | — |
| p03 | 5 | Four phone-only; one at both sizes |
| p04 | 1 | Phone |
| Total | 7 | |

Materia's large pagination overflows the phone screen. Lux has an overflowing heading, table and pagination row, a covered file label on phones, and a 3 px mismatch between attached upload-control segments at both sizes. The dashboard keeps its expanded sidebar on phones and squeezes the content into a 100 px panel. No visible layout defects were found on Grayscale.

The individual records in findings.json include exact selectors, measurements, suggested fixes and screenshot filenames. Screenshot sequences and contact sheets are saved beside this report; scroll-records.json records the scroll positions.
