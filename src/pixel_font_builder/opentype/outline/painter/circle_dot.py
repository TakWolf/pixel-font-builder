from __future__ import annotations

import math

from pixel_font_builder.glyph import Glyph
from pixel_font_builder.opentype.outline.painter.base import OutlinesPainter
from pixel_font_builder.opentype.outline.pen.base import OutlinesPen


class CircleDotOutlinesPainter(OutlinesPainter):
    radius: float

    def __init__(self, radius: float = 0.4):
        self.radius = radius

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CircleDotOutlinesPainter):
            return NotImplemented
        return self.radius == other.radius

    def draw_outlines(self, glyph: Glyph, pen: OutlinesPen, px_to_units: int):
        radius = self.radius * px_to_units
        c = radius * 4 / 3 * (math.sqrt(2) - 1)
        for y, bitmap_row in enumerate(glyph.bitmap):
            y = (glyph.height + glyph.horizontal_offset_y - y - 0.5) * px_to_units
            for x, pixel in enumerate(bitmap_row):
                x = (x + glyph.horizontal_offset_x + 0.5) * px_to_units
                if pixel != 0:
                    pen.move_to((x, y + radius))
                    pen.cubic_curve_to((x + c, y + radius), (x + radius, y + c), (x + radius, y))
                    pen.cubic_curve_to((x + radius, y - c), (x + c, y - radius), (x, y - radius))
                    pen.cubic_curve_to((x - c, y - radius), (x - radius, y - c), (x - radius, y))
                    pen.cubic_curve_to((x - radius, y + c), (x - c, y + radius), (x, y + radius))
                    pen.close_path()

    def copy(self) -> CircleDotOutlinesPainter:
        return CircleDotOutlinesPainter(self.radius)

    def deepcopy(self) -> CircleDotOutlinesPainter:
        return self.copy()
