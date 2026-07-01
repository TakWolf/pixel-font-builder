from __future__ import annotations

from io import BytesIO
from os import PathLike
from typing import BinaryIO

from fontTools.ttLib import TTFont

from pixel_font_builder.dfont.resource import Resource

_DEFAULT_RESOURCE_ID = 128


class DFontBuilder:
    font: TTFont
    font_size: int
    ascent: int
    descent: int
    line_gap: int
    width_max: int
    is_monospaced: bool
    sfnt_resource_id: int

    def __init__(
            self,
            font: TTFont,
            font_size: int = 0,
            ascent: int = 0,
            descent: int = 0,
            line_gap: int = 0,
            width_max: int = 0,
            is_monospaced: bool = False,
            sfnt_resource_id: int = _DEFAULT_RESOURCE_ID,
    ):
        self.font = font
        self.font_size = font_size
        self.ascent = ascent
        self.descent = descent
        self.line_gap = line_gap
        self.width_max = width_max
        self.is_monospaced = is_monospaced
        self.sfnt_resource_id = sfnt_resource_id

    def build_resources(self) -> list[Resource]:
        if 'name' in self.font:
            tb_name = self.font['name']
            family_name = tb_name.getBestFamilyName()
            postscript_name = tb_name.getDebugName(6)
        else:
            family_name = None
            postscript_name = None

        resources = [
            Resource.create_sfnt(self.sfnt_resource_id, self.font, family_name),
        ]

        if self.font_size > 0:
            resources.append(Resource.create_nfnt(
                self.sfnt_resource_id + self.font_size,
                self.font_size,
                self.ascent,
                self.descent,
                self.line_gap,
                self.is_monospaced,
            ))

        resources.append(Resource.create_fond(
            self.sfnt_resource_id,
            self.font_size,
            self.ascent,
            self.descent,
            self.line_gap,
            self.width_max,
            self.is_monospaced,
            family_name,
            postscript_name,
        ))

        return resources

    def dump(self, stream: BinaryIO):
        resources = self.build_resources()
        Resource.dump(stream, resources)

    def dump_to_bytes(self) -> bytes:
        stream = BytesIO()
        self.dump(stream)
        return stream.getvalue()

    def save(self, file_path: str | PathLike[str]):
        with open(file_path, 'wb') as file:
            self.dump(file)
