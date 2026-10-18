"""Metamorphic relations for the deterministic checks (STF-13).

There is no ground truth for most ergonomic verdicts, but some relations must hold
whatever the true answer is: mirroring the screen and the hand mirrors reach;
making a target bigger never makes it harder to hit; contrast is symmetric; equal
physical size gives equal size verdicts on different phones.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
import _paths  # noqa: E402,F401  (puts the skill folder on sys.path)

from ergoqa import checks, params  # noqa: E402
from ergoqa.devices import css_px_to_mm, get_device  # noqa: E402
from ergoqa.hf import perception, pointing, reach  # noqa: E402
from test_ergo_fixes import ctx, el, profile  # noqa: E402


class Mirror(unittest.TestCase):
    def test_reach_mirrors_with_hand(self) -> None:
        geom = reach.geometry_for_device(get_device("galaxy-s24"))
        for x in (5, 20, 40, 60):
            for y in (10, 50, 90, 130):
                right = reach.reach_score(x, y, geom, "one_hand_right", 107)["difficulty"]
                left = reach.reach_score(geom.screen_w - x, y, geom, "one_hand_left", 107)["difficulty"]
                self.assertAlmostEqual(right, left, places=6, msg=(x, y))

    def test_reach_finding_mirrors_on_the_screen(self) -> None:
        dev = get_device("galaxy-s24")
        vw = dev.viewport_css[0]
        box = (20, 60, 60, 48)
        mirrored = (vw - box[0] - box[2], box[1], box[2], box[3])
        a = checks.check_reach(ctx([el("b", "button", box, text="확인", interactive=True, roles=("primary",), tag="button")], profile(grip="one_hand_right")))
        b = checks.check_reach(ctx([el("b", "button", mirrored, text="확인", interactive=True, roles=("primary",), tag="button")], profile(grip="one_hand_left")))
        self.assertEqual([(o.check_id, o.passed, o.severity) for o in a], [(o.check_id, o.passed, o.severity) for o in b])


class MonotoneSize(unittest.TestCase):
    def test_bigger_targets_are_never_harder_to_hit(self) -> None:
        for k in (1.0, 1.3, 1.69, 2.25):
            prev = 0.0
            for w in (3, 4, 5, 6, 7, 8, 9, 10, 12, 15):
                p = pointing.dual_gaussian_hit_probability(w, w, k)
                self.assertGreaterEqual(p, prev)
                prev = p

    def test_scaling_a_target_up_adds_no_pointing_finding(self) -> None:
        prof = profile(grip="one_hand_right")
        for base in ((20, 700, 30, 30), (20, 700, 40, 36), (20, 700, 100, 44)):
            small = el("b", "button", base, text="다음", interactive=True, roles=("primary",), tag="button")
            big = el("b", "button", (base[0], base[1] - 20, base[2] * 1.25, base[3] * 1.25), text="다음", interactive=True, roles=("primary",), tag="button")
            fail_small = {o.check_id for o in checks.check_target_size(ctx([small], prof)) + checks.check_touch_accuracy(ctx([small], prof)) if not o.passed}
            fail_big = {o.check_id for o in checks.check_target_size(ctx([big], prof)) + checks.check_touch_accuracy(ctx([big], prof)) if not o.passed}
            self.assertLessEqual(fail_big, fail_small, base)


class Symmetry(unittest.TestCase):
    def test_contrast_is_symmetric(self) -> None:
        for a, b in (("#1a73e8", "#ffffff"), ("#b3261e", "#fdecec"), ("#777777", "#000000")):
            ca, cb = perception.parse_color(a), perception.parse_color(b)
            self.assertAlmostEqual(perception.contrast_ratio(ca, cb), perception.contrast_ratio(cb, ca), places=9)

    def test_contrast_verdict_ignores_non_causal_profile_attributes(self) -> None:
        text = el("t", "paragraph", (10, 10, 200, 20), text="회색 안내 문구입니다", fg="#9e9e9e", bg="#ffffff")
        base = {(o.check_id, o.severity) for o in checks.check_contrast(ctx([text], profile()))}
        for variant in (profile(grip="one_hand_left"), profile(age_band="70s+", presbyopia=True), profile(cvd="deutan")):
            self.assertEqual({(o.check_id, o.severity) for o in checks.check_contrast(ctx([text], variant)) if o.check_id == "PC-01"},
                             {x for x in base if x[0] == "PC-01"})


class DeviceInvariance(unittest.TestCase):
    def test_equal_physical_size_gives_equal_size_verdict(self) -> None:
        for mm in (4.0, 6.0, 8.0, 10.0):
            verdicts = set()
            for device_id in ("galaxy-s24", "iphone-15", "pixel-8"):
                dev = get_device(device_id)
                px = mm / css_px_to_mm(dev, 1.0, "x")
                button = el("b", "button", (100, 600, px, px), text="확인", interactive=True, roles=("primary",), tag="button")
                obs = [o for o in checks.check_target_size(ctx([button], profile(device_id=device_id, grip="cradle_right"), device_id)) if o.check_id == "PT-02"]
                verdicts.add(tuple(sorted((o.severity or "-") for o in obs)))
            self.assertEqual(len(verdicts), 1, (mm, verdicts))


if __name__ == "__main__":
    unittest.main()
