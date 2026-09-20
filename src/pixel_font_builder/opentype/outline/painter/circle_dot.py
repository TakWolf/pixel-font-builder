from __future__ import annotations

import math

from pixel_font_builder.glyph import Glyph
from pixel_font_builder.opentype.outline.painter.painter import OutlinePainter
from pixel_font_builder.opentype.outline.pen.pen import OutlinePen


class CircleDotOutlinePainter(OutlinePainter):
    radius: float

    def __init__(self, radius: float = 0.4) -> None:
        self.radius = radius

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CircleDotOutlinePainter):
            return NotImplemented
        return self.radius == other.radius

    def draw_outlines(self, glyph: Glyph, pen: OutlinePen, px_to_units: int) -> None:
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

    def copy(self) -> CircleDotOutlinePainter:
        return CircleDotOutlinePainter(self.radius)

    def deepcopy(self) -> CircleDotOutlinePainter:
        return self.copy()
