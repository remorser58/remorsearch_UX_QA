"""Device catalog completeness and CSS px <-> mm geometry."""
import json
import math
import unittest
from dataclasses import replace

import _paths  # noqa: F401  (puts the skill folder on sys.path)
from ergoqa.devices import (FORM_FACTORS, INPUTS, REQUIRED_IDS, body_mm_to_css_point, css_px_to_mm,
                            css_to_body_mm_point, css_to_display_mm_point, device_for_snapshot,
                            display_mm_from_diagonal, display_offset_mm, get_device, list_devices,
                            mm_per_css_px, mm_to_css_px, rotate)


class CatalogTests(unittest.TestCase):
    def test_required_devices_present_and_unique(self):
        ids = [d.id for d in list_devices()]
        self.assertEqual(len(ids), len(set(ids)))
        for device_id in REQUIRED_IDS:
            self.assertIn(device_id, ids)

    def test_fields_are_well_formed(self):
        for d in list_devices():
            with self.subTest(d.id):
                self.assertIn(d.form_factor, FORM_FACTORS)
                self.assertIn(d.input, INPUTS)
                self.assertIn("http", d.source)
                self.assertGreater(d.dpr, 0)
                self.assertGreater(d.viewing_distance_mm, 0)
                self.assertTrue(all(v > 0 for v in d.viewport_css + d.physical_mm + d.display_mm + d.display_px))
                self.assertGreater(d.diagonal_in, 0)
                portrait = d.viewport_css[0] < d.viewport_css[1]
                self.assertEqual(d.orientation, "portrait" if portrait else "landscape")
                self.assertEqual(d.display_px[0] < d.display_px[1], portrait)
                self.assertEqual(d.physical_mm[0] < d.physical_mm[1], portrait)

    def test_display_fits_inside_body(self):
        for d in list_devices():
            with self.subTest(d.id):
                self.assertLess(d.display_mm[0], d.physical_mm[0])
                self.assertLess(d.display_mm[1], d.physical_mm[1])
                ox, oy = display_offset_mm(d)
                self.assertGreaterEqual(ox, 0)
                self.assertGreaterEqual(oy, 0)

    def test_display_aspect_matches_pixel_aspect_and_diagonal(self):
        for d in list_devices():
            with self.subTest(d.id):
                self.assertAlmostEqual(d.display_mm[0] / d.display_mm[1], d.display_px[0] / d.display_px[1], delta=0.005)
                self.assertAlmostEqual(math.hypot(*d.display_mm) / 25.4, d.diagonal_in, delta=0.05)

    def test_viewport_matches_panel_width(self):
        # Catalog viewport is the full CSS screen; width must equal display_px / dpr (+-1 CSS px).
        for d in list_devices():
            with self.subTest(d.id):
                self.assertAlmostEqual(d.viewport_css[0], d.display_px[0] / d.dpr, delta=1.0)
                self.assertAlmostEqual(d.viewport_css[1], d.display_px[1] / d.dpr, delta=0.015 * d.viewport_css[1])

    def test_diagonal_formula_against_published_ppi(self):
        # Published ppi: iPhone 15 460, iPhone 15 Pro Max 460, Pixel 8 428, Fold6 inner 374.
        for device_id, ppi in (("iphone-15", 460), ("iphone-15-pro-max", 460), ("pixel-8", 428),
                               ("galaxy-z-fold6-inner", 374)):
            with self.subTest(device_id):
                d = get_device(device_id)
                self.assertAlmostEqual(d.display_mm[0], d.display_px[0] / ppi * 25.4, delta=0.01 * d.display_mm[0])
        w, h = display_mm_from_diagonal(10.0, 3, 4)
        self.assertAlmostEqual(w, 152.4)
        self.assertAlmostEqual(h, 203.2)
        with self.assertRaises(ValueError):
            display_mm_from_diagonal(0, 1080, 2340)

    def test_to_dict_is_json_serialisable(self):
        for d in list_devices():
            data = json.loads(json.dumps(d.to_dict()))
            self.assertEqual(data["id"], d.id)
            self.assertEqual(len(data["viewport_css"]), 2)
            self.assertEqual(len(data["display_offset_mm"]), 2)
            self.assertIn("has_touch", data)

    def test_unknown_device(self):
        with self.assertRaises(KeyError):
            get_device("nokia-3310")
        self.assertIs(get_device(get_device("pixel-8")), get_device("pixel-8"))


class ConversionTests(unittest.TestCase):
    def test_round_trip_every_device_and_axis(self):
        for d in list_devices():
            for axis in ("x", "y"):
                for px in (0, 1, 24, 48, 333.5):
                    with self.subTest(d.id, axis=axis, px=px):
                        self.assertAlmostEqual(mm_to_css_px(d, css_px_to_mm(d, px, axis), axis), px, places=9)

    def test_known_values(self):
        # Galaxy S24: 65.99 mm / 360 CSS px -> 48 CSS px is about 8.8 mm.
        self.assertAlmostEqual(css_px_to_mm("galaxy-s24", 48), 8.8, delta=0.05)
        # Square pixels: same pitch on both axes.
        for d in list_devices():
            self.assertAlmostEqual(mm_per_css_px(d, "x"), mm_per_css_px(d, "y"), delta=1e-3)
        with self.assertRaises(ValueError):
            css_px_to_mm("galaxy-s24", 10, axis="z")

    def test_display_and_body_points(self):
        d = get_device("iphone-15")
        self.assertEqual(css_to_display_mm_point(d, 0, 0), (0.0, 0.0))
        x, y = css_to_display_mm_point(d, *d.viewport_css)
        self.assertAlmostEqual(x, d.display_mm[0], delta=0.05)
        self.assertAlmostEqual(y, d.display_mm[1], delta=0.05)
        bx, by = css_to_body_mm_point(d, d.viewport_css[0] / 2, d.viewport_css[1] / 2)
        self.assertAlmostEqual(bx, d.physical_mm[0] / 2, delta=0.05)
        self.assertAlmostEqual(by, d.physical_mm[1] / 2, delta=0.05)
        cx, cy = body_mm_to_css_point(d, bx, by)
        self.assertAlmostEqual(cx, d.viewport_css[0] / 2, places=6)
        self.assertAlmostEqual(cy, d.viewport_css[1] / 2, places=6)

    def test_explicit_display_and_viewport_offsets(self):
        d = replace(get_device("galaxy-s24"), display_offset_mm=(2.0, 1.0), viewport_offset_css=(0.0, 24.0))
        self.assertEqual(display_offset_mm(d), (2.0, 1.0))
        x, y = css_to_body_mm_point(d, 0, 0)
        self.assertAlmostEqual(x, 2.0)
        self.assertAlmostEqual(y, 1.0 + css_px_to_mm(d, 24, "y"))
        self.assertEqual(tuple(round(v, 6) for v in body_mm_to_css_point(d, x, y)), (0.0, 0.0))


class RotationTests(unittest.TestCase):
    def test_landscape_swaps_geometry(self):
        d = get_device("galaxy-s24")
        land = rotate(d)
        self.assertEqual(land.orientation, "landscape")
        self.assertEqual(land.viewport_css, (780, 360))
        self.assertEqual(land.physical_mm, (147.0, 70.6))
        self.assertEqual(land.display_mm, (d.display_mm[1], d.display_mm[0]))
        self.assertAlmostEqual(mm_per_css_px(land, "x"), mm_per_css_px(d, "y"))
        back = rotate(land, "portrait")
        self.assertEqual(back.viewport_css, d.viewport_css)
        self.assertEqual(back.physical_mm, d.physical_mm)
        self.assertIs(rotate(land, "landscape"), land)

    def test_rotation_preserves_physical_location(self):
        # CCW turn: portrait body point (x, y) must land at (y, W - x) in landscape body coordinates.
        d = replace(get_device("galaxy-s24"), display_offset_mm=(1.5, 2.5))
        land = rotate(d)
        body_w = d.physical_mm[0]
        screen_w_css = d.screen_css[0]
        for px, py in ((0, 0), (100, 700), (359, 10)):
            bx, by = css_to_body_mm_point(d, px, py)
            lx, ly = css_to_body_mm_point(land, py, screen_w_css - px)
            with self.subTest(px=px, py=py):
                self.assertAlmostEqual(lx, by, places=6)
                self.assertAlmostEqual(ly, body_w - bx, places=6)
        back = rotate(land, "portrait")
        self.assertEqual(tuple(round(v, 6) for v in back.display_offset_mm), (1.5, 2.5))

    def test_fixed_orientation_devices(self):
        for device_id in ("desktop-1920", "laptop-1440", "tv-55-1080", "switch-handheld"):
            d = get_device(device_id)
            self.assertIs(rotate(d, "landscape"), d)
            with self.assertRaises(ValueError):
                rotate(d, "portrait")
        with self.assertRaises(ValueError):
            rotate("galaxy-s24", "upside-down")

    def test_device_for_snapshot(self):
        land = device_for_snapshot({"id": "pixel-8", "orientation": "landscape"})
        self.assertEqual(land.orientation, "landscape")
        self.assertEqual(device_for_snapshot({"id": "pixel-8", "orientation": "portrait"}), get_device("pixel-8"))


if __name__ == "__main__":
    unittest.main()
