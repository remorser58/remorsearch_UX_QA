# UI QA review — run1, phone 360x780 and laptop 1440x900

Reviewed all 10 saved pages at both viewports and scrolled each page from top to bottom. Findings are limited to visible layout defects; intentional horizontal scrolling inside code blocks and tables was only reported where the content is materially hidden without a usable affordance.

| Page | Findings | Viewports |
| --- | ---: | --- |
| p01 | 1 | phone |
| p02 | 0 | — |
| p03 | 1 | phone |
| p04 | 2 | phone |
| p05 | 1 | both |
| p06 | 2 | phone / both |
| p07 | 1 | phone |
| p08 | 1 | phone |
| p09 | 1 | phone |
| p10 | 1 | phone |

Total: 11 findings. The most visible page-level problems are p01's oversized article screenshots forcing a 586 px document, p07's two hero buttons overlapping, p08's form controls extending past the viewport, and p10's clipped headline and menu label.

Evidence was captured with Playwright/Chromium at 360x780 with touch emulation and at 1440x900. Screenshots are in `shots/` and the raw geometry dump is `diagnostics.json`.

