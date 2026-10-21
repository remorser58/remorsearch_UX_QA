# UI QA review — run3 pages

Reviewed all eight saved pages at 360x780 with touch emulation and at 1440x900, scrolling each page to the end. Nine findings in total; p02 is clean.

| Page | Findings |
| --- | --- |
| p01 | 1 — phone: comparison table is 474px wide in a 326px column, so the last two columns are cut at the viewport edge |
| p02 | 0 |
| p03 | 2 — phone: 'Contents' overflows its 65px sidebar onto the page title; page width is 413px so the nav toggle and a long link run past the 360px edge |
| p04 | 2 — phone: feature table spans x=-28.6..388.6 (417px), cutting both edge columns and adding sideways scroll; form textarea reaches x=389 while its form ends at 347 |
| p05 | 1 — both: the 'Basic progress bar' block is 2288px wide on phone and 2534px on laptop, so text runs off-screen and the page scrolls sideways about 1.9k px |
| p06 | 1 — phone: hero install snippet is 610px wide in 360px, cut at the right edge; the same width pushes the nav 'menu' label off-screen |
| p07 | 1 — phone: 6px sideways scroll from off-canvas nav controls at x=365..397 |
| p08 | 1 — phone: nav links have no horizontal gap ('TextEmbedded contentForm elements') because a:last-child { margin-right: 0 } matches every link |

p02 and p08 share the same markup with different CSS versions; only p08 loses the nav spacing, which points to the a:last-child rule added in that version.

Not tested: Safari/WebKit, real devices, keyboard and assistive technology, hover and open overlay states. All findings are confirmed by screenshot and measured boxes in Chromium.
