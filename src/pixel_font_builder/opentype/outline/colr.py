from collections.abc import Mapping, Sequence, Iterator

from pixel_font_builder.glyph import Glyph, MonoRaster, ColorRaster
from pixel_font_builder.utils.color import ColorRgba


def _iter_color_layers(glyph_name: str, raster: ColorRaster) -> Iterator[tuple[ColorRgba, MonoRaster]]:
    positions = dict[ColorRgba, list[tuple[int, int]]]()

    for y, bitmap_row in enumerate(raster.bitmap):
        if len(bitmap_row) != raster.width:
            raise ValueError(f'color bitmap for glyph {glyph_name!r} must be rectangular: row {y} has {len(bitmap_row)} pixels, expected {raster.width}')

        for x, pixel in enumerate(bitmap_row):
            if not isinstance(pixel, (tuple, list)) or len(pixel) != 4 or any(not isinstance(channel, int) or not 0 <= channel <= 255 for channel in pixel):
                raise ValueError(f'invalid RGBA pixel for glyph {glyph_name!r} at ({x}, {y}): expected four integers in [0, 255]')

            if pixel[3] != 0:
                positions.setdefault(tuple(pixel), []).append((x, y))

    if not positions:
        # An explicit transparent layer prevents fallback to the base outline.
        yield (0, 0, 0, 0), MonoRaster(
            horizontal_offset=(raster.horizontal_offset_x, raster.height + raster.horizontal_offset_y - 1),
            vertical_offset=raster.vertical_offset,
            bitmap=[[1]],
        )
        return

    for color, pixels in positions.items():
        left = min(x for x, _ in pixels)
        right = max(x for x, _ in pixels)
        top = min(y for _, y in pixels)
        bottom = max(y for _, y in pixels)
        bitmap = [[0] * (right - left + 1) for _ in range(bottom - top + 1)]

        for x, y in pixels:
            bitmap[y - top][x - left] = 1

        yield color, MonoRaster(
            horizontal_offset=(raster.horizontal_offset_x + left, raster.horizontal_offset_y + raster.height - bottom - 1),
            vertical_offset=(raster.vertical_offset_x + left, raster.vertical_offset_y + top),
            bitmap=bitmap,
        )


def create_color_outline_glyphs(
        glyph_order: Sequence[str],
        name_to_glyph: Mapping[str, Glyph],
) -> tuple[dict[str, Glyph], dict[str, list[tuple[str, int]]], list[tuple[float, float, float, float]]]:
    layer_glyphs = {}
    color_layers = {}
    palette = []
    palette_indices = {}
    next_layer_index = 0
    for glyph_name in glyph_order:
        glyph = name_to_glyph[glyph_name]
        if glyph.color_raster is None:
            continue

        layers = []
        for color, raster in _iter_color_layers(glyph_name, glyph.color_raster):
            if len(glyph_order) + len(layer_glyphs) >= 65535:
                raise ValueError(f'COLR glyph count exceeds 65535 while adding layers for glyph {glyph_name!r}')

            if color not in palette_indices:
                # 0xFFFF is reserved for the foreground color, not a CPAL entry.
                if len(palette) >= 65535:
                    raise ValueError(f'COLR palette exceeds 65535 colors for glyph {glyph_name!r}')

                palette_indices[color] = len(palette)
                palette.append(tuple(channel / 255 for channel in color))

            while True:
                layer_name = f'.color.{next_layer_index}'
                next_layer_index += 1
                if layer_name not in name_to_glyph:
                    break

            layer_glyphs[layer_name] = Glyph(
                name=layer_name,
                advance_width=glyph.advance_width,
                advance_height=glyph.advance_height,
                mono_raster=raster,
            )
            layers.append((layer_name, palette_indices[color]))
        color_layers[glyph_name] = layers
    return layer_glyphs, color_layers, palette
