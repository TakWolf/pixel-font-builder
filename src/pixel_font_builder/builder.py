from collections import UserList
from os import PathLike

import bdffont
import fontTools.fontBuilder
import fontTools.ttLib
import pcffont

from pixel_font_builder import opentype, bdf, pcf
from pixel_font_builder.glyph import Glyph
from pixel_font_builder.meta import MetaInfo
from pixel_font_builder.metric import FontMetric


class FontBuilder:
    font_metric: FontMetric
    meta_info: MetaInfo
    glyphs: list[Glyph]
    character_mapping: dict[int, str]
    kerning_values: dict[tuple[str, str], int]
    opentype_config: opentype.Config
    bdf_config: bdf.Config
    pcf_config: pcf.Config

    def __init__(self):
        self.font_metric = FontMetric()
        self.meta_info = MetaInfo()
        self.glyphs = []
        self.character_mapping = {}
        self.kerning_values = {}
        self.opentype_config = opentype.Config()
        self.bdf_config = bdf.Config()
        self.pcf_config = pcf.Config()

    def prepare_glyphs(self) -> tuple[list[str], dict[str, Glyph]]:
        glyph_order = ['.notdef']
        name_to_glyph = {}

        for glyph in self.glyphs:
            if glyph.name in name_to_glyph:
                raise RuntimeError(f'duplicate glyphs: {repr(glyph.name)}')
            if glyph.name != '.notdef':
                glyph_order.append(glyph.name)
            name_to_glyph[glyph.name] = glyph

        if '.notdef' not in name_to_glyph:
            raise RuntimeError("missing glyph: '.notdef'")

        for code_point, glyph_name in self.character_mapping.items():
            if code_point < 0:
                raise RuntimeError('code points must >= 0')
            if glyph_name not in name_to_glyph:
                raise RuntimeError(f'missing glyph: {repr(glyph_name)}')

        for (left_glyph_name, right_glyph_name), _ in self.kerning_values.items():
            if left_glyph_name not in name_to_glyph:
                raise RuntimeError(f'missing glyph: {repr(left_glyph_name)}')
            if right_glyph_name not in name_to_glyph:
                raise RuntimeError(f'missing glyph: {repr(right_glyph_name)}')

        return glyph_order, name_to_glyph

    def to_otf_builder(self, flavor: opentype.Flavor | None = None) -> fontTools.fontBuilder.FontBuilder:
        return opentype.create_font_builder(self, False, flavor)

    def save_otf(
            self,
            file_path: str | PathLike[str],
            flavor: opentype.Flavor | None = None,
    ):
        self.to_otf_builder(flavor).save(file_path)

    def to_ttf_builder(self, flavor: opentype.Flavor | None = None) -> fontTools.fontBuilder.FontBuilder:
        return opentype.create_font_builder(self, True, flavor)

    def save_ttf(
            self,
            file_path: str | PathLike[str],
            flavor: opentype.Flavor | None = None,
    ):
        self.to_ttf_builder(flavor).save(file_path)

    def to_bdf_builder(self) -> bdffont.BdfFont:
        return bdf.create_font_builder(self)

    def save_bdf(self, file_path: str | PathLike[str]):
        self.to_bdf_builder().save(file_path)

    def to_pcf_builder(self) -> pcffont.PcfFontBuilder:
        return pcf.create_font_builder(self)

    def save_pcf(self, file_path: str | PathLike[str]):
        self.to_pcf_builder().save(file_path)


class FontCollectionBuilder(UserList[FontBuilder]):
    def to_otc_builder(self) -> fontTools.ttLib.TTCollection:
        return opentype.create_font_collection_builder(self, False)

    def save_otc(
            self,
            file_path: str | PathLike[str],
            share_tables: bool = True,
    ):
        self.to_otc_builder().save(file_path, share_tables)

    def to_ttc_builder(self) -> fontTools.ttLib.TTCollection:
        return opentype.create_font_collection_builder(self, True)

    def save_ttc(
            self,
            file_path: str | PathLike[str],
            share_tables: bool = True,
    ):
        self.to_ttc_builder().save(file_path, share_tables)
