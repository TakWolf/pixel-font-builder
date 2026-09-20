from fontTools.misc.psCharStrings import T2CharString as OtfGlyph
from fontTools.pens.t2CharStringPen import T2CharStringPen as OtfGlyphPen

from pixel_font_builder.opentype.outline.pen.pen import OutlinePen


class OtfOutlinePen(OutlinePen):
    pen: OtfGlyphPen

    def __init__(self, advance_width: int) -> None:
        self.pen = OtfGlyphPen(advance_width, None)

    def move_to(self, point: tuple[float, float]) -> None:
        self.pen.moveTo(point)

    def line_to(self, point: tuple[float, float]) -> None:
        self.pen.lineTo(point)

    def cubic_curve_to(
            self,
            control_point_1: tuple[float, float],
            control_point_2: tuple[float, float],
            end_point: tuple[float, float],
    ) -> None:
        self.pen.curveTo(control_point_1, control_point_2, end_point)

    def quadratic_curve_to(
            self,
            control_point: tuple[float, float],
            end_point: tuple[float, float],
    ) -> None:
        self.pen.qCurveTo(control_point, end_point)

    def end_path(self) -> None:
        self.pen.endPath()

    def close_path(self) -> None:
        self.pen.closePath()

    def to_glyph(self) -> OtfGlyph:
        return self.pen.getCharString()
