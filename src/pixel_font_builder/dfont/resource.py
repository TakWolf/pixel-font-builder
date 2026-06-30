from __future__ import annotations

import struct
from io import BytesIO
from typing import BinaryIO

from fontTools.ttLib import TTFont

_DATA_OFFSET = 0x100


def _pack_fixed(value: int, scale: int) -> int:
    if scale == 0:
        return 0
    return round(value * (1 << 12) / scale)


def _pack_uint24(value: int) -> bytes:
    if value < 0 or value > 0xFFFFFF:
        raise ValueError(f'resource data offset out of range: {value}')
    return value.to_bytes(3, 'big')


def _encode_pascal_string(value: str | None) -> bytes:
    encoded = (value or '').encode('mac_roman', errors='replace')[:255]
    if len(encoded) > 0 and 0x61 <= encoded[0] <= 0x7A:
        encoded = bytes([encoded[0] - 0x20]) + encoded[1:]
    return bytes([len(encoded)]) + encoded


class Resource:
    @staticmethod
    def create_sfnt(
            id: int,
            font: TTFont,
            family_name: str | None,
    ) -> Resource:
        data = BytesIO()
        font.save(data)
        data = data.getvalue()

        return Resource('sfnt', id, data, family_name)

    @staticmethod
    def create_nfnt(
            id: int,
            font_size: int,
            ascent: int,
            descent: int,
            line_gap: int,
            is_monospaced: bool,
    ) -> Resource:
        data = bytearray()
        data.extend(struct.pack('>H', 0xF000 if is_monospaced else 0xD000))
        data.extend(struct.pack('>HH', 0, 255))
        data.extend(struct.pack('>HhHHH', max(font_size, 1), 1, -min(descent, 0), max(font_size, 1), max(font_size, 1)))
        data.extend(struct.pack('>HHHH', 0, max(ascent, 0), max(-descent, 0), max(line_gap, 0)))
        data.extend(struct.pack('>H', 0))
        data = bytes(data)

        return Resource('NFNT', id, data)

    @staticmethod
    def create_fond(
            id: int,
            font_size: int,
            ascent: int,
            descent: int,
            line_gap: int,
            width_max: int,
            is_monospaced: bool,
            family_name: str | None,
    ) -> Resource:
        line_height = max(ascent - descent, 1)
        font_size = font_size if 0 < font_size < 256 else 0

        data = bytearray()

        data.extend(struct.pack('>HHHH', 0x9000 if is_monospaced else 0x1000, id, 0, 255))
        data.extend(struct.pack(
            '>hhhh',
            _pack_fixed(ascent, line_height),
            _pack_fixed(-descent, line_height),
            _pack_fixed(line_gap, line_height),
            _pack_fixed(max(width_max, 1), line_height),
        ))

        offsets_start = len(data)
        data.extend(b'\x00' * 12)
        data.extend(b'\x00' * 18)
        data.extend(struct.pack('>IH', 0, 2))

        associations = [
            (0, 0, id),
        ]
        if font_size > 0:
            associations.append((font_size, 0, id + font_size))
        data.extend(struct.pack('>H', len(associations) - 1))
        for point_size, style, association_id in associations:
            data.extend(struct.pack('>HHH', point_size, style, association_id))
        data.extend(struct.pack('>HL', 0, 6))
        data.extend(struct.pack(
            '>HHhhhh',
            0,
            0,
            0,
            0,
            _pack_fixed(max(width_max, 1), line_height),
            _pack_fixed(max(ascent, 1), line_height),
        ))

        width_offset = len(data)
        data.extend(struct.pack('>HH', 0, 0))
        data.extend(struct.pack('>h', 1 << 12) * 257)

        style_offset = len(data)
        data.extend(struct.pack('>HLL', 0x0005, 0, 0))
        data.extend(bytes([1]) * 48)
        data.extend(struct.pack('>H', 1))
        data.extend(_encode_pascal_string(family_name))

        data[offsets_start:offsets_start + 12] = struct.pack('>LLL', width_offset, 0, style_offset)

        data = bytes(data)

        return Resource('FOND', id, data, family_name)

    @staticmethod
    def dump(stream: BinaryIO, resources: list[Resource]):
        stream.write(b'\x00' * _DATA_OFFSET)
        resource_offsets = []
        for resource in resources:
            resource_offsets.append(stream.tell() - _DATA_OFFSET)
            stream.write(struct.pack('>I', len(resource.data)))
            stream.write(resource.data)

        map_offset = stream.tell()
        resource_types = []
        for resource in resources:
            if resource.type not in resource_types:
                resource_types.append(resource.type)

        type_count = len(resource_types)
        type_list_offset = 28
        type_list_start = map_offset + type_list_offset
        reference_list_start = type_list_start + 2 + type_count * 8
        reference_list_offsets = {}
        cursor = reference_list_start
        for resource_type in resource_types:
            reference_list_offsets[resource_type] = cursor - type_list_start
            cursor += sum(1 for resource in resources if resource.type == resource_type) * 12

        name_list_start = cursor
        name_offsets = {}
        name_data = bytearray()
        for resource in resources:
            if resource.name is None:
                continue
            encoded_name = resource.name.encode('mac_roman')
            if len(encoded_name) > 255:
                raise ValueError(f'resource name too long: {resource.name!r}')
            name_offsets[id(resource)] = len(name_data)
            name_data.append(len(encoded_name))
            name_data.extend(encoded_name)

        resource_map = bytearray()
        resource_map.extend(b'\x00' * 16)
        resource_map.extend(b'\x00' * 4)
        resource_map.extend(b'\x00' * 2)
        resource_map.extend(struct.pack('>HHH', 0, type_list_offset, name_list_start - map_offset))
        resource_map.extend(struct.pack('>H', type_count - 1))

        for resource_type in resource_types:
            type_resources = [resource for resource in resources if resource.type == resource_type]
            resource_map.extend(resource_type.encode('mac_roman'))
            resource_map.extend(struct.pack('>HH', len(type_resources) - 1, reference_list_offsets[resource_type]))

        for resource_type in resource_types:
            for index, resource in ((index, resource) for index, resource in enumerate(resources) if resource.type == resource_type):
                name_offset = name_offsets.get(id(resource), -1)
                resource_map.extend(struct.pack('>hhB', resource.id, name_offset, resource.attributes))
                resource_map.extend(_pack_uint24(resource_offsets[index]))
                resource_map.extend(b'\x00' * 4)

        resource_map.extend(name_data)
        map_length = len(resource_map)
        data_length = map_offset - _DATA_OFFSET

        stream.write(resource_map)
        end_offset = stream.tell()
        stream.seek(0)
        stream.write(struct.pack('>IIII', _DATA_OFFSET, map_offset, data_length, map_length))
        stream.seek(end_offset)

    type: str
    id: int
    data: bytes
    name: str | None
    attributes: int

    def __init__(
            self,
            type: str,
            id: int,
            data: bytes,
            name: str | None = None,
            attributes: int = 0,
    ):
        self.type = type
        self.id = id
        self.data = data
        self.name = name
        self.attributes = attributes
