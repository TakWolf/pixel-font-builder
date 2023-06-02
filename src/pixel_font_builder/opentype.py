from fontTools.fontBuilder import FontBuilder

from pixel_font_builder import font
from pixel_font_builder.info import OpenTypeFlavor


def create_builder(context: 'font.FontBuilder', is_ttf: bool, flavor: OpenTypeFlavor) -> FontBuilder:
    units_per_em = context.size * context.opentype_configs.px_to_units

    builder = FontBuilder(units_per_em, isTTF=is_ttf)

    # TODO

    if flavor is not None:
        builder.font.flavor = flavor

    return builder
