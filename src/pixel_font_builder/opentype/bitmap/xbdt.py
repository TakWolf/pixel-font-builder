from __future__ import annotations

from collections.abc import Mapping
from typing import Generic, TypeVar

from fontTools.ttLib.tables.BitmapGlyphMetrics import BigGlyphMetrics, SmallGlyphMetrics
from fontTools.ttLib.tables.E_B_L_C_ import SbitLineMetrics, BitmapSizeTable

from pixel_font_builder.glyph import Glyph, MonoRaster, ColorRaster
from pixel_font_builder.metric import FontMetric, LineMetric

RasterT = TypeVar('RasterT', MonoRaster, ColorRaster)


class RasterGlyph(Generic[RasterT]):
    @staticmethod
    def create_mono(glyph: Glyph) -> RasterGlyph[MonoRaster]:
        return RasterGlyph(
            glyph.advance_width,
            glyph.advance_height,
            glyph.mono_raster if glyph.mono_raster is not None else MonoRaster(),
        )

    @staticmethod
    def create_color(
            glyph: Glyph,
            ensure_non_empty_bitmap: bool = False,
    ) -> RasterGlyph[ColorRaster]:
        assert glyph.color_raster is not None

        raster = glyph.color_raster
        if ensure_non_empty_bitmap and (raster.width == 0 or raster.height == 0):
            raster = raster.copy()
            # Keep the original top edge and vertical origin when adding a transparent pixel.
            raster.horizontal_offset_y += raster.height - 1
            raster.bitmap = [[(0, 0, 0, 0)]]

        return RasterGlyph(
            glyph.advance_width,
            glyph.advance_height,
            raster,
        )

    advance_width: int
    advance_height: int
    raster: RasterT

    def __init__(
            self,
            advance_width: int,
            advance_height: int,
            raster: RasterT,
    ) -> None:
        self.advance_width = advance_width
        self.advance_height = advance_height
        self.raster = raster


def _create_horizontal_sbit_line_metrics(
        horizontal_layout: LineMetric,
        name_to_glyph: Mapping[str, RasterGlyph],
) -> SbitLineMetrics:
    line_metrics = SbitLineMetrics()
    line_metrics.ascender = horizontal_layout.ascent
    line_metrics.descender = horizontal_layout.descent
    line_metrics.widthMax = max((
        glyph.raster.width
        for glyph in name_to_glyph.values()
    ), default=0)
    line_metrics.caretSlopeNumerator = 1
    line_metrics.caretSlopeDenominator = 0
    line_metrics.caretOffset = 0
    line_metrics.minOriginSB = min((
        glyph.raster.horizontal_offset_x
        for glyph in name_to_glyph.values()
    ), default=0)
    line_metrics.minAdvanceSB = min((
        glyph.advance_width - glyph.raster.horizontal_offset_x - glyph.raster.width
        for glyph in name_to_glyph.values()
    ), default=0)
    line_metrics.maxBeforeBL = max((
        glyph.raster.horizontal_offset_y + glyph.raster.height
        for glyph in name_to_glyph.values()
    ), default=0)
    line_metrics.minAfterBL = min((
        glyph.raster.horizontal_offset_y
        for glyph in name_to_glyph.values()
    ), default=0)
    line_metrics.pad1 = 0
    line_metrics.pad2 = 0
    return line_metrics


def _create_vertical_sbit_line_metrics(
        vertical_layout: LineMetric,
        name_to_glyph: Mapping[str, RasterGlyph],
) -> SbitLineMetrics:
    line_metrics = SbitLineMetrics()
    line_metrics.ascender = vertical_layout.ascent
    line_metrics.descender = vertical_layout.descent
    line_metrics.widthMax = max((
        glyph.raster.height
        for glyph in name_to_glyph.values()
    ), default=0)
    line_metrics.caretSlopeNumerator = 0
    line_metrics.caretSlopeDenominator = 1
    line_metrics.caretOffset = 0
    line_metrics.minOriginSB = min((
        glyph.raster.vertical_offset_y
        for glyph in name_to_glyph.values()
    ), default=0)
    line_metrics.minAdvanceSB = min((
        glyph.advance_height - glyph.raster.vertical_offset_y - glyph.raster.height
        for glyph in name_to_glyph.values()
    ), default=0)
    line_metrics.maxBeforeBL = max((
        glyph.raster.vertical_offset_x + glyph.raster.width
        for glyph in name_to_glyph.values()
    ), default=0)
    line_metrics.minAfterBL = min((
        glyph.raster.vertical_offset_x
        for glyph in name_to_glyph.values()
    ), default=0)
    line_metrics.pad1 = 0
    line_metrics.pad2 = 0
    return line_metrics


def _create_empty_sbit_line_metrics() -> SbitLineMetrics:
    line_metrics = SbitLineMetrics()
    line_metrics.ascender = 0
    line_metrics.descender = 0
    line_metrics.widthMax = 0
    line_metrics.caretSlopeNumerator = 0
    line_metrics.caretSlopeDenominator = 0
    line_metrics.caretOffset = 0
    line_metrics.minOriginSB = 0
    line_metrics.minAdvanceSB = 0
    line_metrics.maxBeforeBL = 0
    line_metrics.minAfterBL = 0
    line_metrics.pad1 = 0
    line_metrics.pad2 = 0
    return line_metrics


def create_bitmap_size_table(
        font_metric: FontMetric,
        name_to_glyph: Mapping[str, RasterGlyph],
        has_vertical_metrics: bool,
        bit_depth: int,
) -> BitmapSizeTable:
    bitmap_size_table = BitmapSizeTable()
    bitmap_size_table.colorRef = 0
    bitmap_size_table.hori = _create_horizontal_sbit_line_metrics(font_metric.horizontal_layout, name_to_glyph)
    if has_vertical_metrics:
        bitmap_size_table.vert = _create_vertical_sbit_line_metrics(font_metric.vertical_layout, name_to_glyph)
    else:
        bitmap_size_table.vert = _create_empty_sbit_line_metrics()
    bitmap_size_table.ppemX = font_metric.font_size
    bitmap_size_table.ppemY = font_metric.font_size
    bitmap_size_table.bitDepth = bit_depth
    bitmap_size_table.flags = 0b_11 if has_vertical_metrics else 0b_01
    return bitmap_size_table


def create_big_glyph_metrics(glyph: RasterGlyph) -> BigGlyphMetrics:
    metrics = BigGlyphMetrics()
    metrics.height = glyph.raster.height
    metrics.width = glyph.raster.width
    metrics.horiBearingX = glyph.raster.horizontal_offset_x
    metrics.horiBearingY = glyph.raster.height + glyph.raster.horizontal_offset_y
    metrics.horiAdvance = glyph.advance_width
    metrics.vertBearingX = glyph.raster.vertical_offset_x
    metrics.vertBearingY = glyph.raster.vertical_offset_y
    metrics.vertAdvance = glyph.advance_height
    return metrics


def create_small_glyph_metrics(glyph: RasterGlyph) -> SmallGlyphMetrics:
    metrics = SmallGlyphMetrics()
    metrics.height = glyph.raster.height
    metrics.width = glyph.raster.width
    metrics.BearingX = glyph.raster.horizontal_offset_x
    metrics.BearingY = glyph.raster.height + glyph.raster.horizontal_offset_y
    metrics.Advance = glyph.advance_width
    return metrics
