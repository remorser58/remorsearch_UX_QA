"""Bounded PNG raster-stream checks for evidence, not capture authentication.

Unlike the per-pixel ergonomics decoder, this gate does not expand an RGBA image.
It checks the complete zlib stream and scanline layout, including Adam7 and all
standard sample depths. Ancillary metadata is not interpreted. A valid image can
still be fabricated: provenance, timestamps, visual review and task replay remain
separate required checks. Animated PNGs are not single-frame capture evidence.

Format reference: https://www.w3.org/TR/2025/REC-png-3-20250624/
"""
from __future__ import annotations

import struct
import zlib

SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_FILE_BYTES = 32 * 1024 * 1024
MAX_PIXELS = 50_000_000
MAX_SCANLINE_BYTES = 256 * 1024 * 1024
_DEPTHS = {0: (1, 2, 4, 8, 16), 2: (8, 16), 3: (1, 2, 4, 8), 4: (8, 16), 6: (8, 16)}
_CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}
_ADAM7 = ((0, 0, 8, 8), (4, 0, 8, 8), (0, 4, 4, 8), (2, 0, 4, 4),
          (0, 2, 2, 4), (1, 0, 2, 2), (0, 1, 1, 2))


class PNGValidationError(ValueError):
    """The supplied bytes cannot support the claimed static PNG capture."""


def validate_png(raw: bytes, expected_size: tuple[int, int]) -> None:
    """Check static capture bytes with fixed file, pixel and expansion budgets.

    This is raster-stream validation, not a general PNG metadata conformance
    checker or proof that a browser ran. No file, network, or subprocess access.
    """
    if len(raw) > MAX_FILE_BYTES or not raw.startswith(SIGNATURE):
        raise PNGValidationError("bad signature or capture exceeds 32 MiB")
    offset = len(SIGNATURE)
    header = None
    palette_entries = None
    transparency_seen = False
    idat = []
    idat_closed = False
    ended = False
    while offset + 12 <= len(raw):
        size, kind = struct.unpack(">I4s", raw[offset:offset + 8])
        end = offset + 12 + size
        if size > 0x7fffffff or end > len(raw):
            raise PNGValidationError("truncated or oversized chunk")
        if not kind.isalpha() or not 65 <= kind[2] <= 90:
            raise PNGValidationError("invalid chunk name or reserved bit")
        body = raw[offset + 8:end - 4]
        crc = struct.unpack(">I", raw[end - 4:end])[0]
        if zlib.crc32(kind + body) & 0xffffffff != crc:
            raise PNGValidationError("chunk CRC mismatch")
        if header is None:
            if kind != b"IHDR" or size != 13:
                raise PNGValidationError("first chunk must be one 13-byte IHDR")
            width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", body)
            if not 0 < width <= 0x7fffffff or not 0 < height <= 0x7fffffff:
                raise PNGValidationError("invalid image dimensions")
            if (width, height) != expected_size:
                raise PNGValidationError("wrong-size capture")
            if width * height > MAX_PIXELS:
                raise PNGValidationError("capture exceeds pixel budget")
            if depth not in _DEPTHS.get(color, ()) or compression or filtering or interlace not in (0, 1):
                raise PNGValidationError("invalid IHDR sample or encoding fields")
            header = (width, height, depth, color, interlace)
        elif kind == b"IHDR":
            raise PNGValidationError("duplicate IHDR")
        elif kind == b"PLTE":
            if palette_entries is not None or idat or transparency_seen or header[3] in (0, 4):
                raise PNGValidationError("duplicate, late or forbidden PLTE")
            if not 3 <= size <= 768 or size % 3:
                raise PNGValidationError("invalid palette length")
            palette_entries = size // 3
            if header[3] == 3 and palette_entries > 1 << header[2]:
                raise PNGValidationError("palette exceeds indexed bit depth")
        elif kind == b"tRNS":
            if transparency_seen or idat or header[3] in (4, 6):
                raise PNGValidationError("duplicate, late or forbidden tRNS")
            if header[3] == 3:
                if palette_entries is None or not 1 <= size <= palette_entries:
                    raise PNGValidationError("invalid indexed transparency")
            elif size != (2 if header[3] == 0 else 6):
                raise PNGValidationError("invalid transparency length")
            transparency_seen = True
        elif kind == b"IDAT":
            if idat_closed or (header[3] == 3 and palette_entries is None):
                raise PNGValidationError("nonconsecutive IDAT or missing palette")
            idat.append(body)
        elif kind == b"IEND":
            if size or end != len(raw) or not idat:
                raise PNGValidationError("invalid IEND, trailing bytes or missing pixels")
            ended = True
            break
        elif kind in (b"acTL", b"fcTL", b"fdAT"):
            raise PNGValidationError("animated PNG is not a static capture")
        elif 65 <= kind[0] <= 90:
            raise PNGValidationError("unsupported critical chunk")
        if idat and kind != b"IDAT":
            idat_closed = True
        offset = end
    if header is None or not ended:
        raise PNGValidationError("missing or truncated IEND")

    width, height, depth, color, interlace = header
    bits = depth * _CHANNELS[color]
    layout = []
    for x, y, dx, dy in (_ADAM7 if interlace else ((0, 0, 1, 1),)):
        columns = max(0, (width - x + dx - 1) // dx)
        rows = max(0, (height - y + dy - 1) // dy)
        if columns and rows:
            layout.append(((columns * bits + 7) // 8, rows))
    size = sum((stride + 1) * rows for stride, rows in layout)
    if size > MAX_SCANLINE_BYTES:
        raise PNGValidationError("capture exceeds scanline expansion budget")
    inflater = zlib.decompressobj()
    try:
        data = inflater.decompress(b"".join(idat), size + 1)
    except zlib.error as error:
        raise PNGValidationError("corrupt IDAT compression stream") from error
    if len(data) != size or not inflater.eof or inflater.unused_data or inflater.unconsumed_tail:
        raise PNGValidationError("incomplete, extra or wrong-length pixel stream")
    offset = 0
    for stride, rows in layout:
        for _ in range(rows):
            if data[offset] > 4:
                raise PNGValidationError("invalid scanline filter")
            offset += stride + 1
