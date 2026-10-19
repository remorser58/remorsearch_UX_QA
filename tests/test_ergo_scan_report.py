"""scan.md names the checks a failed pass left out, so a missing check is a visible gap."""
from __future__ import annotations

import unittest

import _paths  # noqa: F401
from ergoqa import scan

CLOSED = "browser.newContext: Target page, context or browser has been closed"


class ScanReportGapTests(unittest.TestCase):
    def test_failed_passes_are_named_with_their_checks(self):
        missing = scan.checks_not_run([f"reflow pass failed: {CLOSED}", f"adaptation pass failed: {CLOSED}",
                                       f"focus walk (load) failed: {CLOSED}", "Blocked 2 requests", None])
        self.assertEqual([m.split(":")[0] for m in missing],
                         ["RF-01 reflow at 320 px", "RF-02 text spacing and RF-03 short window", "focus walk"])
        report = scan.render_markdown({"url": "file:///site/pages/a.html", "candidates": [], "coverage": [
            {"device": "galaxy-s24", "recorded": True, "seconds": 3.0, "screens": 2, "page_height_css": 900,
             "deepest_scroll_css": 120, "blocked_requests": 1, "checks_not_run": missing}]})
        self.assertIn("Did not run: RF-01 reflow at 320 px: reflow pass failed", report)
        self.assertIn("outside the page's folder", report)
        self.assertNotIn("--allow-origin", report)

    def test_a_clean_run_reports_no_gap(self):
        self.assertEqual(scan.checks_not_run(["flash sampling off", "Blocked 3 requests"]), [])


if __name__ == "__main__":
    unittest.main()
