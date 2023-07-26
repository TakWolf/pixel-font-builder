import os

import bdffont
import fontTools.fontBuilder
import fontTools.ttLib

from pixel_font_builder import opentype, bdf
from pixel_font_builder.glyph import Glyph
from pixel_font_builder.info import MetaInfos


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

        self.character_mapping = dict[int, str]()
        self._name_to_glyph = dict[str, Glyph]()

        self.meta_infos = MetaInfos()
        self.opentype_configs = opentype.Configs()
        self.bdf_configs = bdf.Configs()

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
        if '.notdef' not in self._name_to_glyph:
            raise Exception("Need to provide a glyph named '.notdef'")
        for code_point, glyph_name in self.character_mapping.items():
            if code_point < 0:
                raise Exception('Code points must >= 0')
            if glyph_name not in self._name_to_glyph:
                raise Exception(f"Missing glyph: '{glyph_name}'")
        for glyph in self._name_to_glyph.values():
            glyph.check_ready()
        if self.meta_infos.version is None:
            raise Exception("Missing meta infos: 'version'")
        if self.meta_infos.family_name is None:
            raise Exception("Missing meta infos: 'family_name'")
        if self.meta_infos.style_name is None:
            raise Exception("Missing meta infos: 'style_name'")

    def to_otf_builder(self, flavor: opentype.Flavor = None) -> fontTools.fontBuilder.FontBuilder:
        return opentype.create_builder(self, False, flavor)

    def save_otf(
            self,
            file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
            flavor: opentype.Flavor = None,
    ):
        self.to_otf_builder(flavor).save(file_path)

    def to_ttf_builder(self, flavor: opentype.Flavor = None) -> fontTools.fontBuilder.FontBuilder:
        return opentype.create_builder(self, True, flavor)

    def save_ttf(
            self,
            file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
            flavor: opentype.Flavor = None,
    ):
        self.to_ttf_builder(flavor).save(file_path)

    def to_bdf_builder(self) -> bdffont.BdfFont:
        return bdf.create_builder(self)

    def save_bdf(
            self,
            file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
            optimize_bitmap: bool = True,
    ):
        self.to_bdf_builder().save(file_path, optimize_bitmap)


class FontCollectionBuilder:
    def __init__(self, font_builders: list[FontBuilder] = None):
        if font_builders is None:
            font_builders = list[FontBuilder]()
        self.font_builders = font_builders

    def to_otc_builder(self) -> fontTools.ttLib.TTCollection:
        return opentype.create_collection_builder(self, False)

    def save_otc(
            self,
            file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
            share_tables: bool = True,
    ):
        self.to_otc_builder().save(file_path, share_tables)

    def to_ttc_builder(self) -> fontTools.ttLib.TTCollection:
        return opentype.create_collection_builder(self, True)

    def save_ttc(
            self,
            file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
            share_tables: bool = True,
    ):
        self.to_ttc_builder().save(file_path, share_tables)
