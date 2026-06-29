from __future__ import annotations

import pixel_font_builder
from pixel_font_builder import opentype
from pixel_font_builder.dfont.builder import DFontBuilder


def create_font_builder(context: pixel_font_builder.FontBuilder) -> DFontBuilder:
    font = opentype.create_font_builder(context, True, opentype.OutlineTableMode.OMIT, opentype.BitmapTableMode.APPLE).font

    config = context.dfont_config

    # TODO

    return DFontBuilder(
        font,
        config.is_monospaced,
    )
