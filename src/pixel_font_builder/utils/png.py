import struct
import zlib

from pixel_font_builder.utils.color import ColorRgba


def _pack_png_chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data))


def encode_png_rgba(width: int, height: int, bitmap: list[list[ColorRgba]]) -> bytes:
    """Encode an 8-bit sRGB RGBA bitmap as a non-interlaced PNG.

    Rows run from top to bottom and pixels from left to right. Channels are
    integers in [0, 255], with RGB values not premultiplied by alpha. Both
    dimensions must be integers in [1, 2147483647], and bitmap dimensions
    must match exactly. The input sequences are not modified.
    """
    for field, value in (('width', width), ('height', height)):
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 0x7FFFFFFF:
            raise ValueError(f'{field} must be an integer in [1, 2147483647], got {value!r}')

    if len(bitmap) != height:
        raise ValueError(f'bitmap has {len(bitmap)} rows, expected {height}')

    rows = bytearray()
    for y, row in enumerate(bitmap):
        if len(row) != width:
            raise ValueError(f'bitmap must be rectangular: row {y} has {len(row)} pixels, expected {width}')

        # PNG filter type None.
        rows.append(0)

        for x, pixel in enumerate(row):
            if not isinstance(pixel, (tuple, list)) or len(pixel) != 4 or any(not isinstance(channel, int) or not 0 <= channel <= 255 for channel in pixel):
                raise ValueError(f'invalid RGBA pixel at ({x}, {y}): expected four integers in [0, 255]')
            rows.extend(pixel)

    header = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    return (
        b'\x89PNG\r\n\x1a\n'
        + _pack_png_chunk(b'IHDR', header)
        + _pack_png_chunk(b'sRGB', b'\x00')
        + _pack_png_chunk(b'IDAT', zlib.compress(rows))
        + _pack_png_chunk(b'IEND', b'')
    )
