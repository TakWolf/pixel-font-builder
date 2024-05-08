import os
from collections import UserList

import bdffont
import fontTools.fontBuilder
import fontTools.ttLib
import pcffont

from pixel_font_builder import opentype, bdf, pcf
from pixel_font_builder.metric import FontMetrics
from pixel_font_builder.meta import MetaInfo
from pixel_font_builder.glyph import Glyph


class FontBuilder:
    def __init__(self):
        self.font_metrics = FontMetrics()
        self.meta_info = MetaInfo()
        self.character_mapping: dict[int, str] = {}
        self.glyphs: list[Glyph] = []
        self.opentype_configs = opentype.Configs()
        self.bdf_configs = bdf.Configs()
        self.pcf_configs = pcf.Configs()

    def prepare_glyphs(self) -> tuple[list[str], dict[str, Glyph]]:
        glyph_order = ['.notdef']
        name_to_glyph = {}

        for glyph in self.glyphs:
            assert glyph.name not in name_to_glyph, f"Duplicate glyphs: '{glyph.name}'"
            if glyph.name != '.notdef':
                glyph_order.append(glyph.name)
            name_to_glyph[glyph.name] = glyph

        assert '.notdef' in name_to_glyph, "Need to provide a glyph named '.notdef'"

        for code_point, glyph_name in self.character_mapping.items():
            assert code_point >= 0, 'Code points must >= 0'
            assert glyph_name in name_to_glyph, f"Missing glyph: '{glyph_name}'"

        return glyph_order, name_to_glyph

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

    def save_bdf(self, file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes]):
        self.to_bdf_builder().save(file_path)

    def to_pcf_builder(self) -> pcffont.PcfFontBuilder:
        return pcf.create_builder(self)

    def save_pcf(self, file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes]):
        self.to_pcf_builder().save(file_path)


class FontCollectionBuilder(UserList[FontBuilder]):
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
