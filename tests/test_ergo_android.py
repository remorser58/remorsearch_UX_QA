"""Android uiautomator parsing and adb argv safety. No device or adb binary is used."""
import re
import tempfile
import unittest
from pathlib import Path

import _paths  # noqa: F401  (puts the skill folder on sys.path)
from ergoqa import png
from ergoqa.drivers import android
from ergoqa.drivers.android import AdbArgError
from ergoqa.snapshot import SnapshotError, sha256_file, validate_snapshot

FIXTURE = Path(__file__).parent / "fixtures" / "ergo" / "android_uiautomator_dump.xml"
SHELL_SAFE = re.compile(r"[A-Za-z0-9_%.,@+=:/\-]+")


def xml_text():
    return FIXTURE.read_text(encoding="utf-8")


def by_selector(elements, selector):
    return next(e for e in elements if e["selector"] == selector)


class ParseTests(unittest.TestCase):
    def test_bounds_and_density(self):
        self.assertEqual(android.parse_bounds("[48,2100][1032,2244]"), (48, 2100, 1032, 2244))
        for bad in ("[1,2][3]", "48,2100,1032,2244", "[5,5][1,1]", None):
            with self.subTest(bad), self.assertRaises(SnapshotError):
                android.parse_bounds(bad)
        self.assertEqual(android.density_scale(480), 3.0)
        self.assertEqual(android.density_scale(420), 2.625)
        self.assertAlmostEqual(android.px_to_dp(1080, 420), 411.428571, places=5)
        for bad in (0, 5000, True, "480"):
            with self.subTest(bad), self.assertRaises(SnapshotError):
                android.density_scale(bad)

    def test_fixture_elements(self):
        elements = android.parse_uiautomator_xml(xml_text(), 480)
        self.assertEqual(len(elements), 17)
        self.assertEqual([e["id"] for e in elements], [f"el-{i}" for i in range(1, 18)])
        pay = by_selector(elements, "resource-id=com.example.shop:id/pay")
        self.assertEqual(pay["box"], {"x": 16.0, "y": 700.0, "w": 328.0, "h": 48.0})
        self.assertEqual((pay["role"], pay["name"], pay["text"], pay["interactive"]), ("button", "결제하기", "결제하기", True))
        self.assertEqual(pay["native"]["bounds_px"], [48, 2100, 1032, 2244])
        self.assertEqual(pay["source"], "uiautomator")
        self.assertEqual(pay["roles"], [])
        delete = by_selector(elements, "resource-id=com.example.shop:id/delete_item")
        self.assertEqual((delete["box"]["w"], delete["box"]["h"], delete["name"]), (24.0, 24.0, "삭제"))
        roles = {e["native"]["resource_id"]: e["role"] for e in elements if e["native"]["resource_id"]}
        self.assertEqual(roles["com.example.shop:id/select_item"], "checkbox")
        self.assertEqual(roles["com.example.shop:id/coupon"], "textbox")
        self.assertEqual(roles["com.example.shop:id/gift_wrap"], "switch")
        self.assertEqual(roles["com.example.shop:id/points"], "slider")
        self.assertEqual(roles["com.example.shop:id/total"], "text")
        self.assertNotIn("com.example.shop:id/spacer", roles)  # zero-area node dropped
        back = by_selector(elements, "content-desc=뒤로")
        self.assertEqual((back["role"], back["native"]["role_basis"]), ("button", "class"))
        compose = by_selector(elements, "content-desc=프로모션 배너 닫기")
        self.assertEqual((compose["role"], compose["native"]["role_basis"]), ("button", "clickable_fallback"))
        slider = by_selector(elements, "resource-id=com.example.shop:id/points")
        self.assertFalse(slider["interactive"])  # kept as an input widget even though not clickable

    def test_privacy_visibility_enabled_viewport(self):
        elements = android.parse_uiautomator_xml(xml_text(), 480)
        pin = by_selector(elements, "resource-id=com.example.shop:id/pin")
        self.assertEqual((pin["text"], pin["name"], pin["native"]["password"]), (None, "", True))
        self.assertFalse(by_selector(elements, "text=숨김 안내")["visible"])
        self.assertFalse(by_selector(elements, "resource-id=com.example.shop:id/apply_coupon")["enabled"])
        self.assertFalse(by_selector(elements, "resource-id=com.example.shop:id/more")["in_viewport"])
        self.assertTrue(pay_in := by_selector(elements, "resource-id=com.example.shop:id/pay")["in_viewport"])
        self.assertTrue(pay_in)

    def test_other_density_and_containers(self):
        elements = android.parse_uiautomator_xml(xml_text(), 420)
        pay = by_selector(elements, "resource-id=com.example.shop:id/pay")
        self.assertAlmostEqual(pay["box"]["w"], 984 / 2.625, places=3)
        everything = android.parse_uiautomator_xml(xml_text(), 480, include_containers=True)
        self.assertGreater(len(everything), len(elements))
        self.assertTrue(any(e["role"] == "list" for e in everything))

    def test_rejects_unsafe_or_malformed_xml(self):
        with self.assertRaisesRegex(SnapshotError, "DTD"):
            android.parse_uiautomator_xml('<!DOCTYPE x [<!ENTITY a "b">]><hierarchy/>', 480)
        with self.assertRaisesRegex(SnapshotError, "hierarchy"):
            android.parse_uiautomator_xml("<root/>", 480)
        with self.assertRaisesRegex(SnapshotError, "invalid"):
            android.parse_uiautomator_xml("<hierarchy><node", 480)
        with self.assertRaisesRegex(SnapshotError, "bounds"):
            android.parse_uiautomator_xml('<hierarchy><node bounds="oops" text="x"/></hierarchy>', 480, screen_px=(10, 10))

    def test_selectors_and_role_assignment(self):
        elements = android.parse_uiautomator_xml(xml_text(), 480)
        pay = by_selector(elements, "resource-id=com.example.shop:id/pay")
        for selector in ("#pay", "resource-id=com.example.shop:id/pay", "text=결제하기", "class=android.widget.Button"):
            self.assertTrue(android.match_selector(pay, selector), selector)
        for selector in ("#pa", "text=", "content-desc=결제하기", "xpath=//x", "#"):
            self.assertFalse(android.match_selector(pay, selector), selector)
        unmatched = android.assign_roles(elements, {"primary": ["#pay"], "destructive": ["content-desc=삭제"],
                                                    "ad_like": ["#banner"], "hud": ["hotspot:h1"]})
        self.assertEqual(unmatched, ["ad_like:#banner"])
        self.assertEqual(pay["roles"], ["primary"])
        self.assertEqual(by_selector(elements, "resource-id=com.example.shop:id/delete_item")["roles"], ["destructive"])


class BuildSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.png = Path(self.tmp.name) / "screen.png"
        png.write_png(self.png, png.new_image(1080, 2340, 3, (255, 255, 255)))

    def test_build_snapshot(self):
        snap = android.build_snapshot(xml_text(), screenshot_path=self.png, device_id="galaxy-s24", density_dpi=480,
                                      run_id="R-and-1", step_index=2, captured_at="2026-09-28T12:00:00Z",
                                      targets={"primary": ["#pay"], "destructive": ["#delete_item"], "ad_like": ["#nope"]})
        self.assertEqual(validate_snapshot(snap), [])
        self.assertEqual(snap["snapshot_id"], "S-R-and-1-002")
        self.assertEqual(snap["device"], {"id": "galaxy-s24", "viewport_css": [360.0, 780.0], "dpr": 3.0, "orientation": "portrait"})
        self.assertEqual(snap["surface"], {"kind": "android", "url": None, "title": None, "app_id": "com.example.shop"})
        self.assertEqual(snap["screenshot"], {"path": "screen.png", "sha256": sha256_file(self.png),
                                              "width_px": 1080, "height_px": 2340})
        self.assertIsNone(snap["focus_point"])
        pay = by_selector(snap["elements"], "resource-id=com.example.shop:id/pay")
        self.assertEqual(pay["roles"], ["primary"])
        self.assertTrue(any("matched no element: ad_like:#nope" in n for n in snap["notes"]))
        self.assertTrue(any("supplied by caller" in n for n in snap["notes"]))

    def test_density_from_catalog_is_labelled(self):
        snap = android.build_snapshot(xml_text(), screenshot_path=self.png, device_id="pixel-8")
        self.assertEqual(snap["device"]["dpr"], 2.625)
        self.assertTrue(any("not measured" in n for n in snap["notes"]))

    def test_landscape_rotation_and_failures(self):
        rotated = xml_text().replace('rotation="0"', 'rotation="1"')
        snap = android.build_snapshot(rotated, screenshot_path=self.png, device_id="galaxy-s24", density_dpi=480)
        self.assertEqual(snap["device"]["orientation"], "landscape")
        with self.assertRaisesRegex(SnapshotError, "not found"):
            android.build_snapshot(xml_text(), screenshot_path=Path(self.tmp.name) / "none.png", device_id="galaxy-s24")
        with self.assertRaises(KeyError):
            android.build_snapshot(xml_text(), screenshot_path=self.png, device_id="nokia-3310")
        with self.assertRaisesRegex(SnapshotError, "unsafe"):
            android.build_snapshot(xml_text(), screenshot_path=self.png, device_id="galaxy-s24", screenshot_ref="../x.png")


class AdbArgvTests(unittest.TestCase):
    def assertShellSafe(self, argv):
        self.assertTrue(all(isinstance(a, str) for a in argv))
        if "shell" in argv:
            for arg in argv[argv.index("shell") + 1:]:
                self.assertRegex(arg, SHELL_SAFE)

    def test_builders(self):
        cases = {
            "tap": (android.tap_argv(100.4, 200.6), ["adb", "shell", "input", "tap", "100", "201"]),
            "swipe": (android.swipe_argv(1, 2, 3, 4, 250), ["adb", "shell", "input", "swipe", "1", "2", "3", "4", "250"]),
            "long": (android.long_press_argv(5, 6), ["adb", "shell", "input", "swipe", "5", "6", "5", "6", "600"]),
            "text": (android.text_argv("hello world 01"), ["adb", "shell", "input", "text", "hello%sworld%s01"]),
            "key": (android.keyevent_argv("KEYCODE_BACK"), ["adb", "shell", "input", "keyevent", "KEYCODE_BACK"]),
            "keycode": (android.keyevent_argv(66), ["adb", "shell", "input", "keyevent", "66"]),
            "screencap": (android.screencap_argv(), ["adb", "exec-out", "screencap", "-p"]),
            "dump": (android.uiautomator_dump_argv(), ["adb", "shell", "uiautomator", "dump", "/sdcard/ergoqa_window_dump.xml"]),
            "cat": (android.read_remote_file_argv("/data/local/tmp/d.xml"), ["adb", "exec-out", "cat", "/data/local/tmp/d.xml"]),
            "wm size": (android.wm_size_argv(), ["adb", "shell", "wm", "size"]),
            "wm density": (android.wm_density_argv(serial="emulator-5554"), ["adb", "-s", "emulator-5554", "shell", "wm", "density"]),
        }
        for name, (argv, expected) in cases.items():
            with self.subTest(name):
                self.assertEqual(argv, expected)
                self.assertShellSafe(argv)
        self.assertEqual(android.tap_argv(1, 1, serial="R5CT10ABCDE", adb="/opt/sdk/platform-tools/adb")[:3],
                         ["/opt/sdk/platform-tools/adb", "-s", "R5CT10ABCDE"])

    def test_text_rejects_shell_metacharacters(self):
        for char in list(";|&$`\\\"'<>()*?![]{}~#%^\n\t") + ["결제", "é"]:
            with self.subTest(repr(char)), self.assertRaises(AdbArgError):
                android.text_argv(f"a{char}b")
        for bad in ("", "-rf", "x" * 1001, None):
            with self.subTest(repr(bad)[:20]), self.assertRaises(AdbArgError):
                android.text_argv(bad)
        self.assertEqual(android.escape_input_text("a-b_c.d@e+f=g:h/i,j"), "a-b_c.d@e+f=g:h/i,j")

    def test_numeric_and_identifier_validation(self):
        bad_calls = [
            lambda: android.tap_argv(-1, 5),
            lambda: android.tap_argv(float("nan"), 5),
            lambda: android.tap_argv(True, 5),
            lambda: android.tap_argv("10", 5),
            lambda: android.tap_argv(1e9, 5),
            lambda: android.swipe_argv(1, 2, 3, 4, 70000),
            lambda: android.swipe_argv(1, 2, 3, 4, 1.5),
            lambda: android.keyevent_argv("KEYCODE_HOME;reboot"),
            lambda: android.keyevent_argv("HOME"),
            lambda: android.keyevent_argv(-3),
            lambda: android.keyevent_argv(True),
            lambda: android.tap_argv(1, 1, serial="abc;reboot"),
            lambda: android.tap_argv(1, 1, serial="a b"),
            lambda: android.tap_argv(1, 1, adb="sh"),
            lambda: android.uiautomator_dump_argv("/sdcard/../system/x.xml"),
            lambda: android.uiautomator_dump_argv("/tmp/x.xml"),
            lambda: android.uiautomator_dump_argv("/sdcard/a b.xml"),
            lambda: android.read_remote_file_argv("/sdcard/x;rm"),
            lambda: android.run_adb(["sh", "-c", "echo"]),
            lambda: android.run_adb([]),
        ]
        for i, call in enumerate(bad_calls):
            with self.subTest(i), self.assertRaises(AdbArgError):
                call()

    def test_wm_output_parsing(self):
        self.assertEqual(android.parse_wm_size("Physical size: 1080x2340\n"), (1080, 2340))
        self.assertEqual(android.parse_wm_size("Physical size: 1440x3120\nOverride size: 1080x2340\n"), (1080, 2340))
        self.assertEqual(android.parse_wm_density("Physical density: 480\n"), 480)
        self.assertEqual(android.parse_wm_density("Physical density: 600\nOverride density: 450\n"), 450)
        with self.assertRaises(SnapshotError):
            android.parse_wm_size("error: no devices/emulators found")
        with self.assertRaises(SnapshotError):
            android.parse_wm_density("Physical density: 5\n")


if __name__ == "__main__":
    unittest.main()
