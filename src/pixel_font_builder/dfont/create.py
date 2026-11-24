from __future__ import annotations

from fractions import Fraction
from io import BytesIO

from dfont import DFont, SfntResource, NfntResource, NfntFontType, FondResource, FondFlags, FondAssociation, FondFontStyle

import pixel_font_builder
from pixel_font_builder import opentype


def _pack_fixed(value: int, scale: int) -> int:
    return round(Fraction(value * (1 << 12), scale))


def create_font_builder(context: pixel_font_builder.FontBuilder) -> DFont:
    font_metric = context.font_metric
    meta_info = context.meta_info
    config = context.dfont_config

    font_metric.validate(has_vertical_metrics=False)
    meta_info.validate()
    config.validate()

    width_max = max((
        glyph.advance_width
        for glyph in context.glyphs
        if glyph.name == '.notdef' or not glyph.is_color_raster_only
    ), default=0)

    font = opentype.create_font_builder(context, True, opentype.OutlineTableMode.OMIT, opentype.BitmapTableMode.APPLE).font

    family_name = font['name'].getDebugName(1)
    fond_font_style = FondFontStyle(font['head' if 'head' in font else 'bhed'].macStyle)
    bitmap_metrics = font['bloc'].strikes[0].bitmapSizeTable.hori

    sfnt_data = BytesIO()
    font.save(sfnt_data)

    sfnt_resource = SfntResource(config.resource_id, sfnt_data.getvalue(), family_name)

    nfnt_resource = NfntResource(
        id=config.resource_id,
        font_type=NfntFontType.create(
            fixed_width=config.is_fixed_width,
            do_not_expand=True,
        ),
        width_max=width_max,
        kern_max=bitmap_metrics.minOriginSB,
        negated_descent=font_metric.horizontal_layout.descent,
        rectangle_width=bitmap_metrics.widthMax,
        rectangle_height=font_metric.horizontal_layout.ascent - font_metric.horizontal_layout.descent,
        ascent=font_metric.horizontal_layout.ascent,
        descent=-font_metric.horizontal_layout.descent,
        leading=font_metric.horizontal_layout.line_gap,
    )

    fond_resource = FondResource(
        id=config.resource_id,
        flags=FondFlags.create(
            ignore_fract_enable=True,
            fixed_width=config.is_fixed_width,
        ),
        family_id=config.resource_id,
        ascent=_pack_fixed(font_metric.horizontal_layout.ascent, font_metric.font_size),
        descent=_pack_fixed(font_metric.horizontal_layout.descent, font_metric.font_size),
        leading=_pack_fixed(font_metric.horizontal_layout.line_gap, font_metric.font_size),
        width_max=_pack_fixed(width_max, font_metric.font_size),
        associations=[
            FondAssociation(
                font_style=fond_font_style,
                font_id=config.resource_id,
            ),
            FondAssociation(
                font_size=font_metric.font_size,
                font_style=fond_font_style,
                font_id=config.resource_id,
            ),
        ],
        name=family_name,
    )

    return DFont([sfnt_resource, nfnt_resource, fond_resource])
