import struct
import zlib

from pixel_font_builder import ColorRgba


def read_png_chunks(data: bytes) -> list[tuple[bytes, bytes]]:
    """Read PNG chunks, including unknown chunks and the final IEND.

    Validate the signature, chunk lengths, CRC checksums, and an empty IEND
    with no trailing data. Raise ValueError for invalid framing. Image
    formats and individual chunk semantics are left to the caller.
    """
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('invalid PNG signature')

    offset = 8
    chunks = []
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError(f'truncated PNG chunk at offset {offset}')
        length, tag = struct.unpack_from('>I4s', data, offset)
        if length > 0x7FFFFFFF:
            raise ValueError(f'invalid PNG chunk length {length} at offset {offset}')
        end = offset + 12 + length
        if end > len(data):
            raise ValueError(f'truncated PNG chunk {tag!r} at offset {offset}')
        payload = data[offset + 8:end - 4]
        checksum = struct.unpack_from('>I', data, end - 4)[0]
        if checksum != zlib.crc32(tag + payload):
            raise ValueError(f'invalid PNG chunk checksum for {tag!r} at offset {offset}')
        chunks.append((tag, payload))
        if tag == b'IEND':
            if length != 0:
                raise ValueError('PNG IEND chunk must be empty')
            if end != len(data):
                raise ValueError('unexpected trailing data after PNG IEND chunk')
            return chunks
        offset = end

    raise ValueError('missing PNG IEND chunk')


def read_png(data: bytes) -> tuple[int, int, list[list[ColorRgba]]]:
    chunks = read_png_chunks(data)

    header = None
    compressed = bytearray()
    for index, (tag, payload) in enumerate(chunks):
        if tag == b'IHDR':
            if header is not None or index != 0 or len(payload) != 13:
                raise ValueError('invalid PNG header')
            header = struct.unpack('>IIBBBBB', payload)
        elif tag == b'IDAT':
            compressed.extend(payload)

    if header is None:
        raise ValueError('missing PNG header')
    width, height, bitdepth, color_type, compression, filtering, interlace = header
    if width == 0 or height == 0 or (bitdepth, color_type, compression, filtering, interlace) != (8, 6, 0, 0, 0):
        raise ValueError('expected a non-interlaced 8-bit RGBA PNG')
    raw = zlib.decompress(compressed)
    stride = width * 4
    if len(raw) != height * (stride + 1):
        raise ValueError('invalid PNG pixel data length')

    bitmap = []
    previous = bytearray(stride)
    for y in range(height):
        start = y * (stride + 1)
        row_filter = raw[start]
        row = bytearray(raw[start + 1:start + 1 + stride])
        if row_filter not in (0, 1, 2, 3, 4):
            raise ValueError(f'unsupported PNG row filter {row_filter}')
        for x in range(stride):
            left = row[x - 4] if x >= 4 else 0
            above = previous[x]
            upper_left = previous[x - 4] if x >= 4 else 0
            if row_filter == 0:
                predictor = 0
            elif row_filter == 1:
                predictor = left
            elif row_filter == 2:
                predictor = above
            elif row_filter == 3:
                predictor = (left + above) // 2
            else:
                prediction = left + above - upper_left
                left_distance = abs(prediction - left)
                above_distance = abs(prediction - above)
                upper_left_distance = abs(prediction - upper_left)
                if left_distance <= above_distance and left_distance <= upper_left_distance:
                    predictor = left
                elif above_distance <= upper_left_distance:
                    predictor = above
                else:
                    predictor = upper_left
            row[x] = (row[x] + predictor) & 255
        bitmap.append([(row[x], row[x + 1], row[x + 2], row[x + 3]) for x in range(0, stride, 4)])
        previous = row
    return width, height, bitmap
