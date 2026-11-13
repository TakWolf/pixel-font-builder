from collections.abc import Mapping, Sequence

from fontTools.misc.roundTools import otRound
from fontTools.ttLib.tables.sbixGlyph import Glyph as SbixGlyph
from fontTools.ttLib.tables.sbixStrike import Strike

from pixel_font_builder.glyph import Glyph, ColorRaster
from pixel_font_builder.metric import FontMetric
from pixel_font_builder.opentype.bitmap.xbdt import RasterGlyph
from pixel_font_builder.opentype.outline.pen.pen import OutlinePen
from pixel_font_builder.utils.png import encode_png_rgba


def _check_integer(value: int, minimum: int, maximum: int, field: str) -> None:
    if not isinstance(value, int) or not minimum <= value <= maximum:
        raise ValueError(f'sbix {field} must be an integer in [{minimum}, {maximum}], got {value!r}')


def draw_sbix_bounds(glyph_name: str, raster: ColorRaster, pen: OutlinePen, px_to_units: int) -> None:
    """Include TrueType bitmap bounds without adding monochrome ink.

    Core Text reports base-outline bounds even for sbix glyphs. Browsers
    using those bounds skip empty glyphs and may clip larger color images.
    Two single-point TrueType contours provide these bounds without edges
    that font smoothing could turn into visible hairlines. CFF engines
    discard these anchors, so this helper is only used for TrueType outlines.
    """
    _check_integer(raster.horizontal_offset_x, -32768, 32767, f'originOffsetX for glyph {glyph_name!r}')
    _check_integer(raster.horizontal_offset_y, -32768, 32767, f'originOffsetY for glyph {glyph_name!r}')

    width, height = raster.dimensions
    if width == 0 or height == 0:
        width = height = 1  # Match the explicit transparent PNG.
    x_min = raster.horizontal_offset_x * px_to_units
    y_min = raster.horizontal_offset_y * px_to_units
    x_max = (raster.horizontal_offset_x + width) * px_to_units
    y_max = (raster.horizontal_offset_y + height) * px_to_units

    for field, value in (('xMin', x_min), ('yMin', y_min), ('xMax', x_max), ('yMax', y_max)):
        _check_integer(value, -32768, 32767, f'bitmap {field} in font units for glyph {glyph_name!r}')

    for point in ((x_min, y_min), (x_max, y_max)):
        pen.move_to(point)
        # TTGlyphPen removes a lone moveTo. The explicit closing point is
        # removed by closePath, leaving one stored point in this contour.
        pen.line_to(point)
        pen.close_path()


def create_sbix_strike(
        font_metric: FontMetric,
        glyph_order: Sequence[str],
        name_to_glyph: Mapping[str, Glyph],
        name_to_glyph_bounds: Mapping[str, tuple[float, float, float, float] | None],
        px_to_units: int,
) -> Strike | None:
    glyph_order = [
        glyph_name
        for glyph_name in glyph_order
        if name_to_glyph[glyph_name].color_raster is not None
    ]
    if not glyph_order:
        return None

    _check_integer(font_metric.font_size, 1, 65535, 'pixels per em')

    name_to_color_glyph = {
        glyph_name: RasterGlyph.create_color(
            name_to_glyph[glyph_name],
            ensure_non_empty_bitmap=True,
        )
        for glyph_name in glyph_order
    }

    strike = Strike(
        ppem=font_metric.font_size,
        resolution=72,
    )
    for glyph_name in glyph_order:
        glyph = name_to_color_glyph[glyph_name]
        bounds = name_to_glyph_bounds[glyph_name]

        x_min, y_min = (0, 0) if bounds is None else bounds[:2]
        offset_x = otRound(glyph.raster.horizontal_offset_x - x_min / px_to_units)
        offset_y = otRound(glyph.raster.horizontal_offset_y - y_min / px_to_units)

        _check_integer(offset_x, -32768, 32767, f'originOffsetX for glyph {glyph_name!r}')
        _check_integer(offset_y, -32768, 32767, f'originOffsetY for glyph {glyph_name!r}')

        png_data = encode_png_rgba(glyph.raster.width, glyph.raster.height, glyph.raster.bitmap)

        strike.glyphs[glyph_name] = SbixGlyph(
            glyphName=glyph_name,
            originOffsetX=offset_x,
            originOffsetY=offset_y,
            graphicType='png ',
            imageData=png_data,
        )
    return strike
