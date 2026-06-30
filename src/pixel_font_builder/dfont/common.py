from __future__ import annotations

import pixel_font_builder
from pixel_font_builder import opentype
from pixel_font_builder.dfont.builder import DFontBuilder


def create_font_builder(context: pixel_font_builder.FontBuilder) -> DFontBuilder:
    font = opentype.create_font_builder(context, True, opentype.OutlineTableMode.OMIT, opentype.BitmapTableMode.APPLE).font

    config = context.dfont_config
    font_metric = context.font_metric
    glyphs = context.glyphs

    width_max = max((glyph.advance_width for glyph in glyphs), default=font_metric.font_size)

    return DFontBuilder(
        font,
        font_metric.font_size,
        font_metric.horizontal_layout.ascent,
        font_metric.horizontal_layout.descent,
        font_metric.horizontal_layout.line_gap,
        width_max,
        config.is_monospaced,
    )
