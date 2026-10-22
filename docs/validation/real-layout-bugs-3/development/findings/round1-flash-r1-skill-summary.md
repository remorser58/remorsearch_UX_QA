# UI QA review — run1 saved pages

Scope: 12 saved local pages, each reviewed at 360x780 (phone, touch) and 1440x900 (laptop), scrolled from top to end. Read-only; no page was modified.

Method: Playwright captures per viewport (full page plus scroll tiles), DOM geometry for horizontal overflow and clipping ancestors, and crops viewed at native scale for pixel confirmation. The skill's ergo scan was started on p01 as a cross-check and then replaced by the direct captures.

Findings: 12 across 8 pages.

| Page | Phone | Laptop | Notes |
| --- | --- | --- | --- |
| p01 | 1 | 0 | Header nav overflows 52px; user avatar off-screen |
| p02 | 1 | 0 | 4px horizontal scroll from header nav padding |
| p03 | 1 | 0 | Sidebar opens over the content and hides its own toggle |
| p04 | 1 | 0 | Static 104px sidebar squeezes the header; avatar cut at the right edge |
| p05 | 0 | 0 | — |
| p06 | 2 | 0 | Search input clipped to 53px; empty-state heading flush to the left edge |
| p07 | 0 | 0 | — |
| p08 | 1 | 0 | Same header overflow as p01; avatar off-screen |
| p09 | 2 | 0 | DataTables 521px wide in a 304px wrapper (549px page scroll); pagination Previous button clipped at the card edge |
| p10 | 0 | 0 | — |
| p11 | 1 | 0 | Plugin table clipped by overflow:hidden; 925px page scroll |
| p12 | 1 | 1 | Message rows 657px/913px wide; subject text cut off at both sizes |

The largest problems: p09, p11 and p12 lose table columns and message subjects off-screen on phones, and p03 ships with a sidebar covering the content with no reachable close control. The p01/p08 header overflow drops the user avatar entirely at 360px.

Gaps: hover and focus states were not exercised, and the scroll tiles stop at the page end rather than sampling every intermediate pixel row.
