from __future__ import annotations

from typing import Generic, TypeVar

from pixel_font_builder.glyph import Glyph, MonoRaster, ColorRaster

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
    def create_color(glyph: Glyph) -> RasterGlyph[ColorRaster]:
        assert glyph.color_raster is not None
        return RasterGlyph(
            glyph.advance_width,
            glyph.advance_height,
            glyph.color_raster,
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
