from fontTools.misc.psCharStrings import T2CharString as OtfGlyph
from fontTools.ttLib.tables._g_l_y_f import Glyph as TtfGlyph

from pixel_font_builder.glyph import Glyph
from pixel_font_builder.opentype.outline.painter.base import OutlinesPainter
from pixel_font_builder.opentype.outline.pen.otf import OtfOutlinesPen
from pixel_font_builder.opentype.outline.pen.ttf import TtfOutlinesPen


def create_normal_xtf_glyphs(
        is_ttf: bool,
        outlines_painter: OutlinesPainter,
        name_to_glyph: dict[str, Glyph],
        px_to_units: int,
) -> tuple[dict[str, OtfGlyph | TtfGlyph], dict[str, tuple[int, int]], dict[str, tuple[int, int]]]:
    xtf_glyphs = {}
    horizontal_metrics = {}
    vertical_metrics = {}
    for glyph_name, glyph in name_to_glyph.items():
        advance_width = glyph.advance_width * px_to_units
        left_side_bearing = (glyph.horizontal_offset_x + glyph.calculate_bitmap_left_padding()) * px_to_units
        horizontal_metrics[glyph_name] = advance_width, left_side_bearing

        advance_height = glyph.advance_height * px_to_units
        top_side_bearing = (glyph.vertical_offset_y + glyph.calculate_bitmap_top_padding()) * px_to_units
        vertical_metrics[glyph_name] = advance_height, top_side_bearing

        pen = TtfOutlinesPen() if is_ttf else OtfOutlinesPen(advance_width)
        outlines_painter.draw_outlines(glyph, pen, px_to_units)
        xtf_glyphs[glyph_name] = pen.to_glyph()
    return xtf_glyphs, horizontal_metrics, vertical_metrics


def create_blank_xtf_glyphs(
        is_ttf: bool,
        name_to_glyph: dict[str, Glyph],
        px_to_units: int,
) -> tuple[dict[str, OtfGlyph | TtfGlyph], dict[str, tuple[int, int]], dict[str, tuple[int, int]]]:
    xtf_glyphs = {}
    horizontal_metrics = {}
    vertical_metrics = {}
    for glyph_name, glyph in name_to_glyph.items():
        advance_width = glyph.advance_width * px_to_units
        left_side_bearing = 0
        horizontal_metrics[glyph_name] = advance_width, left_side_bearing

        advance_height = glyph.advance_height * px_to_units
        top_side_bearing = 0
        vertical_metrics[glyph_name] = advance_height, top_side_bearing

        pen = TtfOutlinesPen() if is_ttf else OtfOutlinesPen(advance_width)
        xtf_glyphs[glyph_name] = pen.to_glyph()
    return xtf_glyphs, horizontal_metrics, vertical_metrics
