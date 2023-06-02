from enum import StrEnum

from fontTools.fontBuilder import FontBuilder

from pixel_font_builder import font


class Configs:
    def __init__(
            self,
            px_to_units: int = 100,
    ):
        self.px_to_units = px_to_units


class Flavor(StrEnum):
    WOFF = 'woff'
    WOFF2 = 'woff2'


def create_builder(context: 'font.FontBuilder', is_ttf: bool, flavor: Flavor) -> FontBuilder:
    units_per_em = context.size * context.opentype_configs.px_to_units

    builder = FontBuilder(units_per_em, isTTF=is_ttf)

    # TODO

    if flavor is not None:
        builder.font.flavor = flavor

    return builder
