"""Adversarial byte-level fixtures, not browser or real-user evidence.

The PNGs are authored here. Passing proves that malformed capture bytes cannot
pass this format gate; it never proves their provenance or a successful UX task.
"""
from __future__ import annotations

import hashlib
import math
import struct
import sys
import tempfile
import unittest
import zlib
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

SKILL = Path(__file__).resolve().parents[1] / 'skills/remorsearch-ux-qa'
sys.path.insert(0, str(SKILL))
from uxloop.io import ContractError, GateStop, parse_json
from uxloop.png_capture import PNGValidationError, validate_png

SIGNATURE = b'\x89PNG\r\n\x1a\n'


def chunk(kind, body):
    return (struct.pack('>I', len(body)) + kind + body
            + struct.pack('>I', zlib.crc32(kind + body) & 0xffffffff))


def ihdr(width=1, height=1, depth=8, color=2, compression=0, filtering=0, interlace=0):
    return chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, depth, color,
                                     compression, filtering, interlace))


def png(stream=None, *, header=None, before=b'', after=b''):
    if stream is None:
        stream = zlib.compress(b'\0\x12\x34\x56')
    return (SIGNATURE + (header or ihdr()) + before + chunk(b'IDAT', stream)
            + after + chunk(b'IEND', b''))


class PNGStreamTests(unittest.TestCase):
    def test_valid_rgb_rgba_grey_and_high_depth(self):
        for color, channels, depths in ((0, 1, (1, 2, 4, 8, 16)),
                                        (2, 3, (8, 16)), (4, 2, (8, 16)),
                                        (6, 4, (8, 16))):
            for depth in depths:
                with self.subTest(color=color, depth=depth):
                    stride = (3 * depth * channels + 7) // 8
                    stream = zlib.compress((b'\0' + bytes(stride)) * 2)
                    validate_png(png(stream, header=ihdr(3, 2, depth, color)), (3, 2))

    def test_all_filter_types(self):
        for filter_type in range(5):
            with self.subTest(filter_type=filter_type):
                validate_png(png(zlib.compress(bytes([filter_type, 1, 2, 3]))), (1, 1))

    def test_valid_indexed_depths_and_transparency(self):
        for depth in (1, 2, 4, 8):
            with self.subTest(depth=depth):
                validate_png(png(zlib.compress(b'\0\0'), header=ihdr(depth=depth, color=3),
                                 before=chunk(b'PLTE', b'\0\0\0') + chunk(b'tRNS', b'\xff')), (1, 1))

    def test_multiple_and_empty_consecutive_idat(self):
        stream = zlib.compress(b'\0\1\2\3')
        image = SIGNATURE + ihdr() + chunk(b'IDAT', b'')
        image += b''.join(chunk(b'IDAT', stream[i:i + 1]) for i in range(len(stream)))
        image += chunk(b'IDAT', b'') + chunk(b'IEND', b'')
        validate_png(image, (1, 1))

    def test_ancillary_metadata_does_not_invalidate_pixels(self):
        validate_png(png(before=chunk(b'tEXt', b'Note\0synthetic'),
                         after=chunk(b'tEXt', b'Note\0still synthetic')), (1, 1))

    def test_adam7_one_by_one_skips_empty_passes(self):
        validate_png(png(header=ihdr(interlace=1)), (1, 1))

    def test_adam7_odd_dimensions(self):
        # Independent hand-calculated pass dimensions for 5x3, RGB8.
        passes = [(1, 1), (1, 1), (0, 0), (1, 1), (3, 1), (2, 2), (5, 1)]
        data = b''.join((b'\0' + bytes(width * 3)) * height for width, height in passes)
        validate_png(png(zlib.compress(data), header=ihdr(5, 3, interlace=1)), (5, 3))

    def test_garbage_compression_with_correct_crc_is_rejected(self):
        with self.assertRaises(PNGValidationError):
            validate_png(png(b'not compressed pixels'), (1, 1))

    def test_missing_zlib_trailer_even_with_full_pixels_is_rejected(self):
        stream = zlib.compress(b'\0\1\2\3')
        for removed in (1, 2, 4):
            with self.subTest(removed=removed), self.assertRaises(PNGValidationError):
                validate_png(png(stream[:-removed]), (1, 1))

    def test_extra_compressed_stream_or_suffix_is_rejected(self):
        stream = zlib.compress(b'\0\1\2\3')
        for suffix in (b'garbage', zlib.compress(b'\0\1\2\3')):
            with self.subTest(suffix=suffix), self.assertRaises(PNGValidationError):
                validate_png(png(stream + suffix), (1, 1))

    def test_wrong_expanded_pixel_lengths_are_rejected(self):
        for data in (b'', b'\0\1\2', b'\0\1\2\3\4', b'\0' * 10000):
            with self.subTest(length=len(data)), self.assertRaises(PNGValidationError):
                validate_png(png(zlib.compress(data)), (1, 1))

    def test_invalid_scanline_filter_is_rejected(self):
        for value in (5, 255):
            with self.subTest(value=value), self.assertRaises(PNGValidationError):
                validate_png(png(zlib.compress(bytes([value, 1, 2, 3]))), (1, 1))

    def test_wrong_dimensions_are_rejected(self):
        with self.assertRaisesRegex(PNGValidationError, 'wrong-size'):
            validate_png(png(), (2, 1))

    def test_crc_and_truncation_are_rejected(self):
        raw = png()
        for damaged in (raw[:-1], raw[:40] + bytes([raw[40] ^ 1]) + raw[41:]):
            with self.subTest(length=len(damaged)), self.assertRaises(PNGValidationError):
                validate_png(damaged, (1, 1))

    def test_duplicate_header_and_unknown_critical_are_rejected(self):
        for extra in (ihdr(), chunk(b'ABCD', b'payload')):
            with self.subTest(extra=extra[:8]), self.assertRaises(PNGValidationError):
                validate_png(png(before=extra), (1, 1))

    def test_illegal_sample_and_encoding_fields_are_rejected(self):
        for args in ({'depth': 4}, {'color': 1}, {'compression': 1}, {'filtering': 1},
                     {'interlace': 2}, {'depth': 16, 'color': 3}):
            with self.subTest(args=args), self.assertRaises(PNGValidationError):
                validate_png(png(header=ihdr(**args)), (1, 1))

    def test_palette_is_required_and_cannot_follow_pixels(self):
        for before, after in ((b'', b''), (b'', chunk(b'PLTE', bytes(3)))):
            with self.subTest(late=bool(after)), self.assertRaises(PNGValidationError):
                validate_png(png(zlib.compress(b'\0\0'), header=ihdr(color=3),
                                 before=before, after=after), (1, 1))

    def test_invalid_palette_and_transparency_are_rejected(self):
        variants = (chunk(b'PLTE', b'\0'), chunk(b'PLTE', bytes(9)),
                    chunk(b'PLTE', bytes(3)) * 2,
                    chunk(b'tRNS', b'\xff'),
                    chunk(b'PLTE', bytes(3)) + chunk(b'tRNS', bytes(2)))
        for before in variants:
            with self.subTest(before=before.hex()), self.assertRaises(PNGValidationError):
                validate_png(png(zlib.compress(b'\0\0'), header=ihdr(color=3, depth=1),
                                 before=before), (1, 1))

    def test_nonconsecutive_idat_is_rejected(self):
        with self.assertRaises(PNGValidationError):
            validate_png(png(after=chunk(b'tEXt', b'Gap\0yes') + chunk(b'IDAT', b'')), (1, 1))

    def test_iend_must_be_empty_last_and_have_pixels(self):
        variants = (png() + b'extra', SIGNATURE + ihdr() + chunk(b'IEND', b''),
                    png()[:-12] + chunk(b'IEND', b'bad'))
        for raw in variants:
            with self.subTest(length=len(raw)), self.assertRaises(PNGValidationError):
                validate_png(raw, (1, 1))

    def test_empty_idat_is_not_pixel_evidence(self):
        with self.assertRaises(PNGValidationError):
            validate_png(png(b''), (1, 1))

    def test_animation_is_not_single_frame_capture_evidence(self):
        for kind in (b'acTL', b'fcTL', b'fdAT'):
            with self.subTest(kind=kind), self.assertRaises(PNGValidationError):
                validate_png(png(before=chunk(kind, bytes(8))), (1, 1))

    def test_chunk_name_and_reserved_bit(self):
        for name in (b'abcd', b'abc1', b'\xffABC'):
            with self.subTest(name=name), self.assertRaises(PNGValidationError):
                validate_png(png(before=chunk(name, b'')), (1, 1))

    def test_budget_rejection_precedes_inflation(self):
        with patch('uxloop.png_capture.zlib.decompressobj') as inflater:
            for size, depth, color in (((10000, 10000), 8, 2), ((7000, 7000), 16, 6)):
                with self.subTest(size=size, depth=depth), self.assertRaises(PNGValidationError):
                    validate_png(png(header=ihdr(*size, depth=depth, color=color)), size)
            inflater.assert_not_called()

    def test_file_budget_rejection(self):
        with patch('uxloop.png_capture.MAX_FILE_BYTES', 16), self.assertRaises(PNGValidationError):
            validate_png(png(), (1, 1))


class JSONBoundaryTests(unittest.TestCase):
    def test_finite_numbers_preserve_json_behavior(self):
        data = parse_json('{"a":1.5,"b":1e308,"c":1e-999,"d":-0.0,"e":123}')
        self.assertEqual(data['a'], 1.5)
        self.assertTrue(math.isfinite(data['b']))
        self.assertEqual(data['c'], 0.0)
        self.assertEqual(math.copysign(1, data['d']), -1)
        self.assertIs(type(data['e']), int)

    def test_exponent_overflow_is_rejected_at_any_depth(self):
        for raw in ('1e999', '-1e999', '{"value":1e309}', '{"nested":[-1e999]}',
                    b'{"value":1e999}'):
            with self.subTest(raw=raw), self.assertRaises(ContractError):
                parse_json(raw)

    def test_existing_constant_duplicate_and_syntax_guards_remain(self):
        for raw in ('NaN', 'Infinity', '-Infinity', '{"x":1,"x":2}', '{bad', b'\xff'):
            with self.subTest(raw=raw), self.assertRaises(ContractError):
                parse_json(raw)


class EvidencePNGIntegrationTests(unittest.TestCase):
    """Runs the actual Evidence path in a complete checkout (including CI)."""
    def setUp(self):
        from uxloop.evidence import Evidence
        self.evidence_class = Evidence
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.packet = {'mode': 'live', 'policy': {'retention_days': 7},
                       'artifacts': [], 'browser_runs': [], 'scenarios': [],
                       'bundle': {'records': {}}}
        self.viewport = {'width': 1, 'height': 1, 'device_scale_factor': 1}

    def evidence(self, raw):
        (self.root / 'capture.png').write_bytes(raw)
        self.packet['artifacts'] = [{'id': 'capture', 'path': 'capture.png',
                                    'sha256': hashlib.sha256(raw).hexdigest(),
                                    'created_at': datetime.now(timezone.utc).isoformat()}]
        return self.evidence_class(self.packet, self.root)

    def test_actual_gate_rejects_valid_crc_but_bad_pixels(self):
        with self.assertRaisesRegex(GateStop, 'Corrupt') as caught:
            self.evidence(png(b'not compressed pixels')).screenshot('capture', self.viewport)
        self.assertEqual(caught.exception.status, 'unknown')

    def test_actual_gate_rejects_missing_zlib_trailer(self):
        with self.assertRaises(GateStop):
            self.evidence(png(zlib.compress(b'\0\1\2\3')[:-4])).screenshot('capture', self.viewport)

    def test_actual_gate_accepts_valid_capture_and_keeps_dimension_guard(self):
        evidence = self.evidence(png())
        evidence.screenshot('capture', self.viewport)
        with self.assertRaisesRegex(GateStop, 'wrong-size'):
            evidence.screenshot('capture', {**self.viewport, 'width': 2})

    def test_live_svg_is_still_rejected(self):
        raw = b'<svg width="1" height="1" data-ux-fixture="true"/>'
        with self.assertRaisesRegex(GateStop, 'must be PNG'):
            self.evidence(raw).screenshot('capture', self.viewport)

    def test_explicit_fixture_svg_is_still_accepted(self):
        self.packet['mode'] = 'fixture'
        self.evidence(b'<svg width="1" height="1" data-ux-fixture="true"/>').screenshot('capture', self.viewport)


if __name__ == '__main__':
    unittest.main()
