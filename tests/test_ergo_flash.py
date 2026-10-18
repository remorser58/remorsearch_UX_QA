"""Block-grid photosensitivity screening (GM-04): WCAG 2.3.1 general and red flashes."""

from __future__ import annotations

import base64
import collections
import random
import unittest

import _paths  # noqa: F401  (puts the skill folder on sys.path)

from ergoqa import checks, params  # noqa: E402
from ergoqa.devices import get_device  # noqa: E402
from ergoqa.hf import game  # noqa: E402

DEVICE = get_device("galaxy-s24")
VW, VH = DEVICE.viewport_css
COLS, ROWS = 16, 20
BW, BH = VW / COLS, VH / ROWS
GRID = {"cols": COLS, "rows": ROWS, "block_css": [BW, BH], "viewport_css": [VW, VH]}


def _overlap(col: int, row: int, box: tuple[float, float, float, float]) -> float:
    x, y, w, h = box
    ox = max(0.0, min(x + w, (col + 1) * BW) - max(x, col * BW))
    oy = max(0.0, min(y + h, (row + 1) * BH) - max(y, row * BH))
    return ox * oy / (BW * BH)


def _u8(values: list[float]) -> str:
    return base64.b64encode(bytes(round(255 * min(1.0, max(0.0, v))) for v in values)).decode()


def samples(frame, times, moved=False):
    """``frame(t, col, row) -> (luminance, red share)`` sampled at ``times`` (ms)."""
    out = []
    for i, t in enumerate(times):
        cells = [frame(t, c, r) for r in range(ROWS) for c in range(COLS)]
        s = {"t_ms": t, "step_index": 0, "block_lum": _u8([c[0] for c in cells]), "block_red": _u8([c[1] for c in cells]),
             "mean_luminance": sum(c[0] for c in cells) / len(cells), "changed_fraction": 1.0}
        if moved and i:
            s["block_moved"] = base64.b64encode(b"\xff" * ((COLS * ROWS + 7) // 8)).decode()
        out.append(s)
    return out


def even(fps: float, seconds: float = 3.0, start: float = 0.0) -> list[float]:
    step = 1000.0 / fps
    return [start + i * step for i in range(int(seconds * fps))]


def jittered(seconds: float = 3.0, base_ms: float = 33.0, jitter_ms: float = 15.0) -> list[float]:
    """Deterministic stand-in for the driver's random pause between captures."""
    t, out, seed = 0.0, [], 12345
    while t < seconds * 1000.0:
        out.append(t)
        seed = (1103515245 * seed + 12345) % (1 << 31)
        t += base_ms + jitter_ms * seed / (1 << 31)
    return out


def square(hz: float):
    """True in the first half of each period of a square wave at ``hz``."""
    half = 500.0 / hz
    return lambda t: int(t // half) % 2 == 0


def box_flash(box, hz, on=1.0, off=0.0, bg=0.5):
    phase = square(hz)

    def frame(t, c, r):
        f = _overlap(c, r, box)
        return (bg * (1 - f) + (on if phase(t) else off) * f, 0.0)
    return frame


def analyse(smp):
    pitch = (DEVICE.display_mm[0] / DEVICE.viewport_css[0], DEVICE.display_mm[1] / DEVICE.viewport_css[1])
    return game.analyse_block_flashes(smp, GRID, pitch, DEVICE.viewing_distance_mm)


class BlockFlash(unittest.TestCase):
    def test_local_box_above_area_threshold_fails(self) -> None:
        # 190 x 120 CSS px at 5 Hz: ~35 x 22 mm at 300 mm, about 0.0085 sr > 0.006 sr.
        res = analyse(samples(box_flash((85, 300, 190, 120), 5), even(30)))
        self.assertTrue(res["failed"], res["general"])
        self.assertGreater(res["general"]["area_sr"], params.FLASH_AREA_SR)
        self.assertGreaterEqual(res["general"]["max_flashes_per_s"], 4)

    def test_same_flash_on_a_small_box_passes(self) -> None:
        res = analyse(samples(box_flash((150, 300, 60, 60), 5), even(30)))
        self.assertFalse(res["failed"])
        self.assertLess(res["general"]["area_sr"], params.FLASH_AREA_SR)
        self.assertGreater(res["general"]["flashing_blocks"], 0)

    def test_counter_phase_halves_fail_although_the_mean_is_constant(self) -> None:
        phase = square(5)
        frame = lambda t, c, r: ((1.0 if phase(t) else 0.0) if r < ROWS // 2 else (0.0 if phase(t) else 1.0), 0.0)  # noqa: E731
        smp = samples(frame, even(30))
        self.assertEqual(game.count_general_flashes(smp)["max_flashes_per_window"], 0.0)  # the old whole-viewport path
        self.assertTrue(analyse(smp)["failed"])

    def test_red_to_grey_full_screen_is_a_red_flash(self) -> None:
        phase = square(5)
        # #ff0000 and #7f7f7f have almost the same relative luminance (0.213 / 0.212).
        frame = lambda t, c, r: (0.2126, 1.0) if phase(t) else (0.212, 0.0)  # noqa: E731
        res = analyse(samples(frame, even(30)))
        self.assertFalse(res["general"]["failed"])
        self.assertTrue(res["red"]["failed"])
        self.assertTrue(res["failed"])

    def test_scrolling_content_is_motion_not_flashing(self) -> None:
        frame = lambda t, c, r: (0.9 if (int(t // 33) + r) % 2 else 0.1, 0.0)  # noqa: E731
        self.assertTrue(analyse(samples(frame, even(30)))["failed"])  # without the motion flags it would fail
        self.assertFalse(analyse(samples(frame, even(30), moved=True))["failed"])

    def test_slow_full_screen_change_passes(self) -> None:
        res = analyse(samples(box_flash((0, 0, VW, VH), 1), even(30)))
        self.assertFalse(res["failed"])
        self.assertFalse(res["extended"])

    def test_three_hertz_is_not_more_than_three_flashes(self) -> None:
        # A 3 Hz flicker has 7 transitions spanning exactly 1 s; sampling at 25 fps
        # detects each up to 40 ms late. It must not fail; 4 Hz must.
        self.assertFalse(analyse(samples(box_flash((0, 0, VW, VH), 3), even(25)))["failed"])
        self.assertTrue(analyse(samples(box_flash((0, 0, VW, VH), 4), even(25)))["failed"])
        self.assertLessEqual(game.count_general_flashes(samples(box_flash((0, 0, VW, VH), 3), even(25)))["max_flashes_per_window"], 3)

    def test_jittered_sampling_sees_a_flicker_that_phase_locked_sampling_aliases(self) -> None:
        frame = box_flash((0, 0, VW, VH), 30)
        locked = analyse(samples(frame, even(30, start=5.0)))  # capture phase-locked to the 30 Hz flicker
        self.assertEqual(locked["general"]["flashing_blocks"], 0)
        self.assertTrue(analyse(samples(frame, jittered()))["failed"])

    def test_sustained_two_hertz_is_an_extended_failure(self) -> None:
        res = analyse(samples(box_flash((0, 0, VW, VH), 2.5), even(30, seconds=6)))
        self.assertFalse(res["failed"])
        self.assertTrue(res["extended"])


def train(flash_hz: float, seconds: float, start: float = 0.0) -> tuple[float, ...]:
    """Transition times of a flicker: two transitions per flash."""
    step = 500.0 / flash_hz
    return tuple(start + k * step for k in range(int(round(seconds * 2 * flash_hz))))


def iris_reference(times, frame=10.0, window=1000.0):
    """Frame-by-frame restatement of EA IRIS TransitionTracker (d96978a) for the test:
    per frame, transitions in the last second; a frame is in band at 4-6; it fails when
    in band with at least 4 s of in-band frames among the last 5 s."""
    fails, history = [], collections.deque(maxlen=int(5000 / frame))
    base = times[0] - frame
    f = 0
    while True:
        f += 1
        t = base + f * frame
        if t > times[-1] + window + frame:
            return fails
        n = sum(1 for x in times if t - window < x <= t + 1e-9)
        band = 4 <= n <= 6
        history.append(band)
        if band and sum(history) >= int(4000 / frame):
            fails.append(round(t, 6))


class IrisExtended(unittest.TestCase):
    """GQA-03: EA IRIS's extended-failure rule next to the sustained 5 s rule."""

    def fail_times(self, times):
        return [round(base + k * 10.0, 6) for r0, r1 in game.iris_extended_runs(times) for base in [r0] for k in range(int(round((r1 - r0) / 10.0)) + 1)]

    def test_brief_boundary_trains(self) -> None:
        cases = {(2, 4): False, (3, 3.4): False, (2.5, 5): True, (2, 3): False, (2, 5): True}
        for (hz, sec), expected in cases.items():
            with self.subTest(hz=hz, seconds=sec):
                self.assertEqual(bool(game.iris_extended_runs(train(hz, sec))), expected)

    def test_matches_the_frame_by_frame_restatement(self) -> None:
        rng = random.Random(7)
        trains = [train(hz, sec) for hz in (1.5, 2, 2.5, 3) for sec in (3, 4, 4.8, 5, 6)]
        for _ in range(40):
            t, out = 0.0, []
            while t < 7000:
                out.append(round(t, 3))
                t += rng.uniform(120, 420)
            trains.append(tuple(out))
        for times in trains:
            with self.subTest(n=len(times), first=times[:3]):
                self.assertEqual(self.fail_times(times), iris_reference(times))

    def test_rules_differ_on_an_uneven_train(self) -> None:
        # 3 flashes/s for 2.5 s, then 1 flash/s: 10 flashes within 5 s (sustained rule)
        # but only about 3 s at 4-6 transitions per second (IRIS rule).
        times = train(3, 2.5) + train(1, 2.5, start=2500.0)
        self.assertLess(times[-1] - times[0], params.FLASH_EXTENDED_WINDOW_MS)
        self.assertGreaterEqual(len(times) / 2, params.FLASH_EXTENDED_MIN_FLASHES)
        self.assertEqual(game.iris_extended_runs(times), ())

    def test_block_grid_reports_both_rules(self) -> None:
        res = analyse(samples(box_flash((0, 0, VW, VH), 2), even(30, seconds=6)))
        self.assertFalse(res["failed"])
        self.assertTrue(res["iris_extended"])
        self.assertTrue(res["extended"])
        short = analyse(samples(box_flash((0, 0, VW, VH), 2), even(30, seconds=3.5)))
        self.assertFalse(short["extended"])
        self.assertTrue(short["iris_warning"])


class GM04Observation(unittest.TestCase):
    def run_with(self, smp, *, steps=None, fps_ok=True):
        return {"run_id": "R-F", "steps": steps or [], "flash_samples": smp,
                "flash_sampling": {"enabled": True, "block_grid": GRID, "truncated": None, "jitter_ms": [0, 15]}}

    def observe(self, run):
        prof = {"profile_id": "EP-F", "attributes": {"device_id": "galaxy-s24", "vision": {"viewing_distance_mm": 300}}}
        return [o for o in checks.check_run_timing(run, prof, DEVICE, {}, None) if o.check_id == "GM-04"]

    def test_block_failure_is_p0_with_location(self) -> None:
        steps = [{"step_index": 0, "t_start_ms": 0, "t_end_ms": 3000, "result": "ok", "action": {"action": "wait", "ms": 3000}}]
        (obs,) = self.observe(self.run_with(samples(box_flash((85, 300, 190, 120), 5), even(30)), steps=steps))
        self.assertEqual(obs.severity, "P0")
        self.assertEqual(obs.measurement["verdict"], "fail")
        self.assertEqual(obs.measurement["method"], "block-grid-v1")
        self.assertEqual(obs.measurement["step_index"], 0)

    def test_pass_with_poor_sampling_is_inconclusive_not_clean(self) -> None:
        (obs,) = self.observe(self.run_with(samples(lambda t, c, r: (0.5, 0.0), even(8))))
        self.assertTrue(obs.passed)
        self.assertEqual(obs.measurement["verdict"], "inconclusive")
        self.assertIn("low_fps", obs.measurement["coverage_problems"])
        self.assertIn("판정 불가", obs.message_ko)

    def test_unsampled_wait_is_reported(self) -> None:
        steps = [{"step_index": 0, "t_start_ms": 0, "t_end_ms": 900, "result": "ok", "action": {"action": "tap", "target": "#go"}},
                 {"step_index": 1, "t_start_ms": 5000, "t_end_ms": 8000, "result": "ok", "action": {"action": "wait", "ms": 3000}}]
        (obs,) = self.observe(self.run_with(samples(lambda t, c, r: (0.5, 0.0), even(30, seconds=0.9)), steps=steps))
        self.assertEqual(obs.measurement["coverage"]["unsampled_animating_steps"], [1])
        self.assertEqual(obs.measurement["verdict"], "inconclusive")

    def test_extended_failure_names_its_rule_and_does_not_defer_to_iris(self) -> None:
        (obs,) = self.observe(self.run_with(samples(box_flash((0, 0, VW, VH), 2), even(30, seconds=6))))
        self.assertEqual(obs.severity, "P1")
        self.assertTrue(obs.measurement["iris_extended"])
        self.assertIn("IRIS 확장 실패 규칙", obs.message_ko)
        self.assertIn("IRIS 통과가 이 판정을 뒤집지 않습니다", obs.message_ko)

    def test_runs_without_a_block_grid_use_the_viewport_mean(self) -> None:
        smp = [{k: v for k, v in s.items() if not k.startswith("block_")} for s in samples(box_flash((0, 0, VW, VH), 5), even(30))]
        run = self.run_with(smp)
        run["flash_sampling"].pop("block_grid")
        (obs,) = self.observe(run)
        self.assertEqual(obs.measurement["method"], "viewport-mean-v1")
        self.assertEqual(obs.severity, "P0")

    def test_viewport_mean_returns_every_key_for_short_series(self) -> None:
        stats = game.count_general_flashes([{"t_ms": 0, "mean_luminance": 0.5}])
        self.assertEqual(set(stats), {"max_flashes_per_window", "max_area_fraction", "transitions", "max_flashes_per_5s", "extended"})


class DomRed(unittest.TestCase):
    def test_saturated_red_uses_linear_channels(self) -> None:
        # (230, 60, 60): 0.66 of the encoded sum, 0.90 of the linear sum.
        self.assertTrue(checks._saturated_red((230, 60, 60)))
        self.assertTrue(checks._saturated_red((255, 0, 0)))
        self.assertFalse(checks._saturated_red((200, 120, 120)))
        self.assertFalse(checks._saturated_red((20, 0, 0)))  # near black: (R-G-B)*320 <= 20
        self.assertFalse(checks._saturated_red(None))


if __name__ == "__main__":
    unittest.main()
