from __future__ import annotations

from pixel_font_builder.glyph import Glyph
from pixel_font_builder.opentype.outline.painter.painter import OutlinePainter
from pixel_font_builder.opentype.outline.pen.pen import OutlinePen


class SquareDotOutlinePainter(OutlinePainter):
    size: float

    def __init__(self, size: float = 0.8) -> None:
        self.size = size

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SquareDotOutlinePainter):
            return NotImplemented
        return self.size == other.size

    def draw_outlines(self, glyph: Glyph, pen: OutlinePen, px_to_units: int) -> None:
        size = self.size * px_to_units
        offset = (1 - self.size) / 2 * px_to_units
        for y, bitmap_row in enumerate(glyph.bitmap):
            y = (glyph.height + glyph.horizontal_offset_y - y) * px_to_units - offset
            for x, pixel in enumerate(bitmap_row):
                x = (x + glyph.horizontal_offset_x) * px_to_units + offset
                if pixel != 0:
                    pen.move_to((x, y))
                    pen.line_to((x + size, y))
                    pen.line_to((x + size, y - size))
                    pen.line_to((x, y - size))
                    pen.close_path()

    def copy(self) -> SquareDotOutlinePainter:
        return SquareDotOutlinePainter(self.size)

    def deepcopy(self) -> SquareDotOutlinePainter:
        return self.copy()
