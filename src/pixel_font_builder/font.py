import datetime
import os

import bdffont
import fontTools.fontBuilder
import fontTools.ttLib
import pcffont

from pixel_font_builder import os2, opentype, bdf, pcf
from pixel_font_builder.glyph import Glyph
from pixel_font_builder.info import MetaInfo, LayoutHeader


class FontBuilder:
    def __init__(self, size: int):
        self.size = size
        self.created_time: datetime.datetime | None = None
        self.modified_time: datetime.datetime | None = None

        self.meta_info = MetaInfo()
        self.horizontal_header = LayoutHeader()
        self.vertical_header = LayoutHeader()
        self.os2_config = os2.Config()
        self.character_mapping: dict[int, str] = {}
        self.glyphs: list[Glyph] = []
        self.opentype_config = opentype.Config()
        self.bdf_config = bdf.Config()
        self.pcf_config = pcf.Config()

    def prepare_glyphs(self) -> tuple[list[str], dict[str, Glyph]]:
        glyph_order = ['.notdef']
        name_to_glyph = {}

        for glyph in self.glyphs:
            assert glyph.name not in name_to_glyph, f"Duplicate glyphs: '{glyph.name}'"
            glyph.check_validity()
            if glyph.name != '.notdef':
                glyph_order.append(glyph.name)
            name_to_glyph[glyph.name] = glyph

        assert '.notdef' in name_to_glyph, "Need to provide a glyph named '.notdef'"

        for code_point, glyph_name in self.character_mapping.items():
            assert code_point >= 0, 'Code points must >= 0'
            assert glyph_name in name_to_glyph, f"Missing glyph: '{glyph_name}'"

        return glyph_order, name_to_glyph

    def to_xtf_builder(self, is_ttf: bool, flavor: opentype.Flavor = None) -> fontTools.fontBuilder.FontBuilder:
        return opentype.create_builder(self, is_ttf, flavor)

    def to_otf_builder(self, flavor: opentype.Flavor = None) -> fontTools.fontBuilder.FontBuilder:
        return self.to_xtf_builder(False, flavor)

    def save_otf(
            self,
            file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
            flavor: opentype.Flavor = None,
    ):
        self.to_otf_builder(flavor).save(file_path)

    def to_ttf_builder(self, flavor: opentype.Flavor = None) -> fontTools.fontBuilder.FontBuilder:
        return self.to_xtf_builder(True, flavor)

    def save_ttf(
            self,
            file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
            flavor: opentype.Flavor = None,
    ):
        self.to_ttf_builder(flavor).save(file_path)

    def to_bdf_builder(self) -> bdffont.BdfFont:
        return bdf.create_font(self)

    def save_bdf(
            self,
            file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
            optimize_bitmap: bool = True,
    ):
        self.to_bdf_builder().save(file_path, optimize_bitmap)

    def to_pcf_builder(self) -> pcffont.PcfFont:
        return pcf.create_font(self)

    def save_pcf(self, file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes]):
        self.to_pcf_builder().save(file_path)


class FontCollectionBuilder:
    def __init__(self, font_builders: list[FontBuilder] = None):
        if font_builders is None:
            font_builders = []
        self.font_builders = font_builders

    def _to_xtf_builders(self, is_ttf: bool) -> list[fontTools.fontBuilder.FontBuilder]:
        return [font_builder.to_xtf_builder(is_ttf) for font_builder in self.font_builders]

    def to_xtc_builder(self, is_ttf: bool) -> fontTools.ttLib.TTCollection:
        return opentype.create_collection_builder(self._to_xtf_builders(is_ttf))

    def to_otc_builder(self) -> fontTools.ttLib.TTCollection:
        return self.to_xtc_builder(False)

    def save_otc(
            self,
            file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
            share_tables: bool = True,
    ):
        self.to_otc_builder().save(file_path, share_tables)

    def to_ttc_builder(self) -> fontTools.ttLib.TTCollection:
        return self.to_xtc_builder(True)

    def save_ttc(
            self,
            file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
            share_tables: bool = True,
    ):
        self.to_ttc_builder().save(file_path, share_tables)
