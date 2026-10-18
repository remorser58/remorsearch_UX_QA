"""Unit tests for the deterministic human-factors models (ergoqa.hf)."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

import _paths  # noqa: E402,F401  (puts the skill folder on sys.path)

from ergoqa.devices import get_device, rotate  # noqa: E402
from ergoqa.hf import cognition, game, gaze, perception, pointing, reach  # noqa: E402


class PerceptionTests(unittest.TestCase):
    def test_contrast_ratio_reference_values(self) -> None:
        self.assertAlmostEqual(perception.contrast_ratio((0, 0, 0), (255, 255, 255)), 21.0, places=6)
        self.assertAlmostEqual(perception.contrast_ratio(perception.parse_color("#777"), (255, 255, 255)), 4.478, places=3)
        self.assertAlmostEqual(perception.contrast_ratio((255, 255, 255), (255, 255, 255)), 1.0)

    def test_large_text_threshold(self) -> None:
        self.assertEqual(perception.required_text_contrast(16, 400), 4.5)
        self.assertEqual(perception.required_text_contrast(24, 400), 3.0)
        self.assertEqual(perception.required_text_contrast(19, 700), 3.0)
        self.assertEqual(perception.required_text_contrast(19, 400), 4.5)

    def test_ciede2000_sharma_pairs(self) -> None:
        pairs = [
            ((50.0, 2.6772, -79.7751), (50.0, 0.0, -82.7485), 2.0425),
            ((50.0, 3.1571, -77.2803), (50.0, 0.0, -82.7485), 2.8615),
            ((50.0, 2.49, -0.001), (50.0, -2.49, 0.0009), 7.1792),
            ((50.0, -0.001, 2.49), (50.0, 0.0009, -2.49), 4.8045),
            ((50.0, -0.001, 2.49), (50.0, 0.0011, -2.49), 4.7461),
            ((50.0, 2.5, 0.0), (73.0, 25.0, -18.0), 27.1492),
            ((60.2574, -34.0099, 36.2677), (60.4626, -34.1751, 39.4387), 1.2644),
        ]
        for lab1, lab2, expected in pairs:
            self.assertAlmostEqual(perception.delta_e_2000(lab1, lab2), expected, places=4)

    def test_red_green_collapses_for_deutan_not_normal(self) -> None:
        red, green = perception.parse_color("#d32f2f"), perception.parse_color("#388e3c")
        self.assertGreater(perception.color_difference(red, green), 40)
        self.assertLess(perception.cvd_difference(red, green, "deutan"), 10)
        # Blue vs orange stays distinguishable for deutan.
        blue, orange = perception.parse_color("#1f77b4"), perception.parse_color("#ff7f0e")
        self.assertGreater(perception.cvd_difference(blue, orange, "deutan"), 20)

    def test_parse_color_variants(self) -> None:
        self.assertEqual(perception.parse_color("rgb(255, 0, 0)"), (255.0, 0.0, 0.0))
        self.assertIsNone(perception.parse_color("rgba(0, 0, 0, 0)"))
        self.assertIsNone(perception.parse_color("transparent"))
        self.assertEqual(perception.parse_color("#abc"), (170.0, 187.0, 204.0))

    def test_visual_angle(self) -> None:
        # 1 mm at 300 mm ~ 11.46 arcmin
        self.assertAlmostEqual(perception.visual_angle_arcmin(1.0, 300), 11.459, places=2)


class PointingTests(unittest.TestCase):
    def test_dual_gaussian_matches_published_derivations(self) -> None:
        expected = {3.0: 0.59, 3.8: 0.74, 5.0: 0.89, 7.0: 0.975, 9.6: 0.997}
        for width, p in expected.items():
            self.assertAlmostEqual(pointing.dual_gaussian_hit_probability(width, width), p, delta=0.006)

    def test_multiplier_reduces_hit_probability(self) -> None:
        base = pointing.dual_gaussian_hit_probability(7, 7, 1.0)
        walking = pointing.dual_gaussian_hit_probability(7, 7, 1.4)
        self.assertLess(walking, base)

    def test_neighbour_misfire_decreases_with_gap(self) -> None:
        target = {"x": 0, "y": 0, "w": 7, "h": 7}
        probs = [pointing.dual_gaussian_neighbour_probability(target, {"x": 7 + g, "y": 0, "w": 7, "h": 7}, 1.4) for g in (0, 1, 2, 4)]
        self.assertTrue(all(a > b for a, b in zip(probs, probs[1:])))
        self.assertAlmostEqual(probs[0], 0.0376, delta=0.002)

    def test_wcag_spacing_exception(self) -> None:
        small = {"x": 0, "y": 0, "w": 20, "h": 20}
        far = {"x": 100, "y": 0, "w": 20, "h": 20}
        near = {"x": 22, "y": 0, "w": 20, "h": 20}
        self.assertEqual(pointing.wcag_target_size_ok(small, [far]), (True, "spacing_exception"))
        self.assertFalse(pointing.wcag_target_size_ok(small, [near])[0])
        self.assertEqual(pointing.wcag_target_size_ok({"x": 0, "y": 0, "w": 24, "h": 24}, [near]), (True, "size"))

    def test_fitts_and_ffitts(self) -> None:
        self.assertAlmostEqual(pointing.fitts_id(7, 1), 3.0)
        self.assertTrue(math.isinf(pointing.ffitts_id(50, 3.0, 1.5)))
        self.assertGreater(pointing.ffitts_id(50, 9.6, 1.3), pointing.fitts_id(50, 9.6))


class ReachTests(unittest.TestCase):
    def setUp(self) -> None:
        self.geom = reach.geometry_for_device(get_device("galaxy-s24"))

    def test_mirror_identity(self) -> None:
        for x, y in ((5, 5), (30, 70), (60, 130), (10, 120)):
            right = reach.one_hand_score(x, y, self.geom, 111, "R")["difficulty"]
            left = reach.one_hand_score(self.geom.screen_w - x, y, self.geom, 111, "L")["difficulty"]
            self.assertAlmostEqual(right, left, places=9)

    def test_far_top_corner_hardest_centre_easy(self) -> None:
        g = self.geom
        far_top = reach.one_hand_score(3, 3, g, 111, "R")["difficulty"]
        centre = reach.one_hand_score(g.screen_w / 2, g.screen_h * 0.6, g, 111, "R")["difficulty"]
        grip_bottom = reach.one_hand_score(g.screen_w - 3, g.screen_h - 3, g, 111, "R")
        self.assertEqual(far_top, 1.0)
        self.assertEqual(centre, 0.0)
        self.assertGreater(grip_bottom["difficulty"], centre)
        self.assertTrue(grip_bottom["cramped"])

    def test_top_band_out_on_large_phone(self) -> None:
        g = reach.geometry_for_device(get_device("galaxy-s24-ultra"))
        self.assertEqual(reach.one_hand_score(g.screen_w / 2, 5, g, 111, "R")["zone"], "out")

    def test_two_thumbs_uses_easier_hand_and_cradle_is_free(self) -> None:
        g = self.geom
        two = reach.reach_score(5, 60, g, "two_thumbs", 111)
        one = reach.reach_score(5, 60, g, "one_hand_right", 111)
        self.assertLessEqual(two["difficulty"], one["difficulty"])
        self.assertEqual(reach.reach_score(5, 5, g, "cradle_right", 111)["difficulty"], 0.0)

    def test_landscape_control_cost(self) -> None:
        device = rotate(get_device("galaxy-s24"), "landscape")
        g = reach.geometry_for_device(device)
        top_right = reach.landscape_control_cost(g.screen_w - 10, 8, g, 25, 22)
        near_rest = reach.landscape_control_cost(g.screen_w - 25, g.screen_h - 22, g, 25, 22)
        self.assertTrue(top_right["top_band"])
        self.assertLess(near_rest["travel_mm"], 1.0)


class GazeTests(unittest.TestCase):
    def test_conspicuity_peaks_at_odd_patch(self) -> None:
        pixels = [[(255, 255, 255)] * 20 for _ in range(20)]
        for y in range(8, 12):
            for x in range(8, 12):
                pixels[y][x] = (220, 30, 30)
        grid = gaze.conspicuity_map(pixels)
        peak = max((v, (x, y)) for y, row in enumerate(grid) for x, v in enumerate(row))
        self.assertTrue(6 <= peak[1][0] <= 13 and 6 <= peak[1][1] <= 13)

    def test_priorities_prefer_large_contrasting_element(self) -> None:
        elements = [
            {"id": "big", "box": {"x": 20, "y": 600, "w": 320, "h": 56}, "font_size_px": 18, "font_weight": 700, "_contrast": 8.0, "interactive": True},
            {"id": "tiny", "box": {"x": 20, "y": 700, "w": 40, "h": 14}, "font_size_px": 11, "font_weight": 400, "_contrast": 2.0},
        ]
        pr = gaze.element_priorities(elements, (360, 780), "phone")
        self.assertGreater(pr["big"], pr["tiny"])
        path = gaze.predicted_scanpath(elements, pr, (360, 780))
        self.assertEqual(path[0], "big")

    def test_eccentricity(self) -> None:
        self.assertAlmostEqual(gaze.eccentricity_deg((0, 0), (0, 100), 300), math.degrees(math.atan2(100, 300)))


class CognitionAndGameTests(unittest.TestCase):
    def test_hick_monotone(self) -> None:
        self.assertLess(cognition.hick_hyman_ms(2), cognition.hick_hyman_ms(12))

    def test_reading_time_counts_hangul(self) -> None:
        self.assertEqual(cognition.reading_units("결제가 완료되었습니다 OK 123"), (10, 2))
        self.assertGreater(cognition.min_display_ms("가" * 60, 300), cognition.min_display_ms("가" * 10, 300))

    def test_latency_bands(self) -> None:
        self.assertEqual(cognition.latency_band(50), "instant")
        self.assertEqual(cognition.latency_band(1500), "needs_progress_indicator")
        self.assertEqual(cognition.latency_band(None), "no_feedback")

    def test_flash_counting(self) -> None:
        # 5 Hz full-screen black/white alternation for 1 s -> 5 flashes.
        samples = [{"t_ms": i * 100, "mean_luminance": 1.0 if i % 2 else 0.0, "changed_fraction": 1.0} for i in range(11)]
        stats = game.count_general_flashes(samples)
        self.assertGreaterEqual(stats["max_flashes_per_window"], 5)
        slow = [{"t_ms": i * 500, "mean_luminance": 1.0 if i % 2 else 0.0, "changed_fraction": 1.0} for i in range(5)]
        self.assertLessEqual(game.count_general_flashes(slow)["max_flashes_per_window"], 1.5)

    def test_flash_area(self) -> None:
        self.assertTrue(game.flash_area_exceeds(1.0, 66, 143, 300))
        self.assertFalse(game.flash_area_exceeds(0.002, 66, 143, 300))

    def test_timing_margin(self) -> None:
        rt95 = game.reaction_time_quantile_ms(450, 90, 0.95)
        self.assertGreater(rt95, 450)
        self.assertLess(game.timing_window_margin_ms(300, rt95, 80), 0)


class ViewTests(unittest.TestCase):
    def test_profile_view_cvd_and_glare(self) -> None:
        from ergoqa import png
        from ergoqa.view import profile_view

        image = png.make_image(4, 1, 3, bytes([211, 47, 47, 56, 142, 60, 0, 0, 0, 255, 255, 255]))
        profile = {"attributes": {"vision": {"cvd": "deutan", "cvd_severity": 1.0}, "context": {"lighting": "bright_sun"}}}
        out, applied = profile_view(image, profile, 1.0)
        self.assertEqual((out.width, out.height), (4, 1))
        self.assertTrue(any("Machado" in a for a in applied))
        red, green, black = out.pixel(0, 0), out.pixel(1, 0), out.pixel(2, 0)
        self.assertLess(abs(red[0] - green[0]) + abs(red[1] - green[1]), 60)
        self.assertGreater(black[0], 100)  # veiling glare lifts black


if __name__ == "__main__":
    unittest.main()
