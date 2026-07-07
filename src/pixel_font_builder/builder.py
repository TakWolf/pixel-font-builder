from __future__ import annotations

from collections import UserList
from os import PathLike
from typing import Any

import bdffont
import fontTools.fontBuilder
import fontTools.ttLib
import pcffont

from pixel_font_builder import opentype, dfont, bdf, pcf
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
    dfont_config: dfont.Config
    bdf_config: bdf.Config
    pcf_config: pcf.Config

    def __init__(self):
        self.font_metric = FontMetric()
        self.meta_info = MetaInfo()
        self.glyphs = []
        self.character_mapping = {}
        self.kerning_values = {}
        self.opentype_config = opentype.Config()
        self.dfont_config = dfont.Config()
        self.bdf_config = bdf.Config()
        self.pcf_config = pcf.Config()

    def __copy__(self) -> FontBuilder:
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any]) -> FontBuilder:
        return self.deepcopy()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FontBuilder):
            return NotImplemented
        return (self.font_metric == other.font_metric and
                self.meta_info == other.meta_info and
                self.glyphs == other.glyphs and
                self.character_mapping == other.character_mapping and
                self.kerning_values == other.kerning_values and
                self.opentype_config == other.opentype_config and
                self.dfont_config == other.dfont_config and
                self.bdf_config == other.bdf_config and
                self.pcf_config == other.pcf_config)

    def prepare_glyphs(self) -> tuple[list[str], dict[str, Glyph]]:
        glyph_order = ['.notdef']
        name_to_glyph = {}

        for glyph in self.glyphs:
            if glyph.name in name_to_glyph:
                raise RuntimeError(f'duplicate glyphs: {glyph.name!r}')
            if glyph.name != '.notdef':
                glyph_order.append(glyph.name)
            name_to_glyph[glyph.name] = glyph

        if '.notdef' not in name_to_glyph:
            raise RuntimeError("missing glyph: '.notdef'")

        for code_point, glyph_name in self.character_mapping.items():
            if code_point < 0:
                raise RuntimeError('code points must >= 0')
            if glyph_name not in name_to_glyph:
                raise RuntimeError(f'missing glyph: {glyph_name!r}')

        for (left_glyph_name, right_glyph_name), _ in self.kerning_values.items():
            if left_glyph_name not in name_to_glyph:
                raise RuntimeError(f'missing glyph: {left_glyph_name!r}')
            if right_glyph_name not in name_to_glyph:
                raise RuntimeError(f'missing glyph: {right_glyph_name!r}')

        return glyph_order, name_to_glyph

    def to_otf_builder(
            self,
            outline_table_mode: opentype.OutlineTableMode = opentype.OutlineTableMode.NORMAL,
            bitmap_table_mode: opentype.BitmapTableMode = opentype.BitmapTableMode.NONE,
            flavor: opentype.Flavor | None = None,
    ) -> fontTools.fontBuilder.FontBuilder:
        return opentype.create_font_builder(self, False, outline_table_mode, bitmap_table_mode, flavor)

    def save_otf(
            self,
            file_path: str | PathLike[str],
            outline_table_mode: opentype.OutlineTableMode = opentype.OutlineTableMode.NORMAL,
            bitmap_table_mode: opentype.BitmapTableMode = opentype.BitmapTableMode.NONE,
            flavor: opentype.Flavor | None = None,
    ):
        self.to_otf_builder(outline_table_mode, bitmap_table_mode, flavor).save(file_path)

    def to_ttf_builder(
            self,
            outline_table_mode: opentype.OutlineTableMode = opentype.OutlineTableMode.NORMAL,
            bitmap_table_mode: opentype.BitmapTableMode = opentype.BitmapTableMode.NONE,
            flavor: opentype.Flavor | None = None,
    ) -> fontTools.fontBuilder.FontBuilder:
        return opentype.create_font_builder(self, True, outline_table_mode, bitmap_table_mode, flavor)

    def save_ttf(
            self,
            file_path: str | PathLike[str],
            outline_table_mode: opentype.OutlineTableMode = opentype.OutlineTableMode.NORMAL,
            bitmap_table_mode: opentype.BitmapTableMode = opentype.BitmapTableMode.NONE,
            flavor: opentype.Flavor | None = None,
    ):
        self.to_ttf_builder(outline_table_mode, bitmap_table_mode, flavor).save(file_path)

    def to_ms_bitmap_ttf_builder(self) -> fontTools.fontBuilder.FontBuilder:
        return self.to_ttf_builder(opentype.OutlineTableMode.BLANK_GLYPHS, opentype.BitmapTableMode.STANDARD)

    def save_ms_bitmap_ttf(self, file_path: str | PathLike[str]):
        self.to_ms_bitmap_ttf_builder().save(file_path)

    def to_otb_builder(self) -> fontTools.fontBuilder.FontBuilder:
        return self.to_ttf_builder(opentype.OutlineTableMode.ZERO_LENGTH, opentype.BitmapTableMode.STANDARD)

    def save_otb(self, file_path: str | PathLike[str]):
        self.to_otb_builder().save(file_path)

    def to_dfont_builder(self) -> dfont.DFontBuilder:
        return dfont.create_font_builder(self)
    
    def save_dfont(self, file_path: str | PathLike[str]):
        self.to_dfont_builder().save(file_path)

    def to_bdf_builder(self) -> bdffont.BdfFont:
        return bdf.create_font_builder(self)

    def save_bdf(self, file_path: str | PathLike[str]):
        self.to_bdf_builder().save(file_path)

    def to_pcf_builder(self) -> pcffont.PcfFontBuilder:
        return pcf.create_font_builder(self)

    def save_pcf(self, file_path: str | PathLike[str]):
        self.to_pcf_builder().save(file_path)

    def copy(self) -> FontBuilder:
        builder = FontBuilder()
        builder.font_metric = self.font_metric
        builder.meta_info = self.meta_info
        builder.glyphs = self.glyphs
        builder.character_mapping = self.character_mapping
        builder.kerning_values = self.kerning_values
        builder.opentype_config = self.opentype_config
        builder.dfont_config = self.dfont_config
        builder.bdf_config = self.bdf_config
        builder.pcf_config = self.pcf_config
        return builder

    def deepcopy(self) -> FontBuilder:
        builder = FontBuilder()
        builder.font_metric = self.font_metric.deepcopy()
        builder.meta_info = self.meta_info.deepcopy()
        builder.glyphs = [glyph.deepcopy() for glyph in self.glyphs]
        builder.character_mapping = self.character_mapping.copy()
        builder.kerning_values = self.kerning_values.copy()
        builder.opentype_config = self.opentype_config.deepcopy()
        builder.dfont_config = self.dfont_config.deepcopy()
        builder.bdf_config = self.bdf_config.deepcopy()
        builder.pcf_config = self.pcf_config.deepcopy()
        return builder


class FontCollectionBuilder(UserList[FontBuilder]):
    def __copy__(self) -> FontCollectionBuilder:
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any]) -> FontCollectionBuilder:
        return self.deepcopy()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FontCollectionBuilder):
            return NotImplemented
        return super().__eq__(other)

    def to_otc_builder(
            self,
            outline_table_mode: opentype.OutlineTableMode = opentype.OutlineTableMode.NORMAL,
            bitmap_table_mode: opentype.BitmapTableMode = opentype.BitmapTableMode.NONE,
    ) -> fontTools.ttLib.TTCollection:
        return opentype.create_font_collection_builder(self, False, outline_table_mode, bitmap_table_mode)

    def save_otc(
            self,
            file_path: str | PathLike[str],
            outline_table_mode: opentype.OutlineTableMode = opentype.OutlineTableMode.NORMAL,
            bitmap_table_mode: opentype.BitmapTableMode = opentype.BitmapTableMode.NONE,
            share_tables: bool = True,
    ):
        self.to_otc_builder(outline_table_mode, bitmap_table_mode).save(file_path, share_tables)

    def to_ttc_builder(
            self,
            outline_table_mode: opentype.OutlineTableMode = opentype.OutlineTableMode.NORMAL,
            bitmap_table_mode: opentype.BitmapTableMode = opentype.BitmapTableMode.NONE,
    ) -> fontTools.ttLib.TTCollection:
        return opentype.create_font_collection_builder(self, True, outline_table_mode, bitmap_table_mode)

    def save_ttc(
            self,
            file_path: str | PathLike[str],
            outline_table_mode: opentype.OutlineTableMode = opentype.OutlineTableMode.NORMAL,
            bitmap_table_mode: opentype.BitmapTableMode = opentype.BitmapTableMode.NONE,
            share_tables: bool = True,
    ):
        self.to_ttc_builder(outline_table_mode, bitmap_table_mode).save(file_path, share_tables)

    def copy(self) -> FontCollectionBuilder:
        return FontCollectionBuilder(self)

    def deepcopy(self) -> FontCollectionBuilder:
        return FontCollectionBuilder((builder.deepcopy() for builder in self))
