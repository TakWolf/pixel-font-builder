import os

import bdffont
import fontTools.fontBuilder

from pixel_font_builder import opentype, bdf
from pixel_font_builder.glyph import Glyph
from pixel_font_builder.info import MetaInfos, OpenTypeConfigs, BdfConfigs


class FontBuilder:
    def __init__(
            self,
            size: int,
            ascent: int,
            descent: int,
            x_height: int = None,
            cap_height: int = None,
    ):
        self.size = size
        self.ascent = ascent
        self.descent = descent
        self.x_height = x_height
        self.cap_height = cap_height

        self.character_mapping: dict[int, str] = {}
        self._name_to_glyph: dict[str, Glyph] = {}

        self.meta_infos = MetaInfos()
        self.opentype_configs = OpenTypeConfigs()
        self.bdf_configs = BdfConfigs()

    @property
    def line_height(self) -> int:
        return self.ascent - self.descent

    def get_glyph(self, name: str) -> Glyph | None:
        return self._name_to_glyph.get(name, None)

    def get_glyphs(self) -> list[Glyph]:
        return list(self._name_to_glyph.values())

    def get_glyphs_count(self) -> int:
        return len(self._name_to_glyph)

    def set_glyph(self, glyph: Glyph):
        self._name_to_glyph[glyph.name] = glyph

    def add_glyph(self, glyph: Glyph):
        if glyph.name in self._name_to_glyph:
            raise Exception(f"Glyph '{glyph.name}' already exists")
        self._name_to_glyph[glyph.name] = glyph

    def add_glyphs(self, glyphs: list[Glyph]):
        for glyph in glyphs:
            self.add_glyph(glyph)

    def remove_glyph(self, name: str) -> Glyph | None:
        return self._name_to_glyph.pop(name, None)

    def check_ready(self):
        if any(code_point < 0 for code_point in self.character_mapping):
            raise Exception(f"Code points must >= 0")
        if '.notdef' not in self._name_to_glyph:
            raise Exception("Need to provide a glyph named '.notdef'")

    def to_otf_builder(self, flavor: opentype.Flavor = None) -> fontTools.fontBuilder.FontBuilder:
        self.check_ready()
        return opentype.create_builder(self, False, flavor)

    def save_otf(
            self,
            file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
            flavor: opentype.Flavor = None,
    ):
        self.to_otf_builder(flavor).save(file_path)

    def to_ttf_builder(self, flavor: opentype.Flavor = None) -> fontTools.fontBuilder.FontBuilder:
        self.check_ready()
        return opentype.create_builder(self, True, flavor)

    def save_ttf(
            self,
            file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
            flavor: opentype.Flavor = None,
    ):
        self.to_ttf_builder(flavor).save(file_path)

    def to_bdf_builder(self) -> bdffont.BdfFont:
        self.check_ready()
        return bdf.create_builder(self)

    def save_bdf(
            self,
            file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
            optimize_bitmap: bool = True,
    ):
        self.to_bdf_builder().save(file_path, optimize_bitmap)
