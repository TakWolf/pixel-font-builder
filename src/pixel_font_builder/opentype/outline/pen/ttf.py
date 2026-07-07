from fontTools import cu2qu
from fontTools.pens.ttGlyphPen import TTGlyphPen as TtfGlyphPen
from fontTools.ttLib.tables._g_l_y_f import Glyph as TtfGlyph

from pixel_font_builder.opentype.outline.pen.base import OutlinesPen


class TtfOutlinesPen(OutlinesPen):
    pen: TtfGlyphPen
    cubic_curve_double_max_err: float
    current_point: tuple[float, float] | None

    def __init__(self, cubic_curve_double_max_err: float = 1):
        self.pen = TtfGlyphPen()
        self.cubic_curve_double_max_err = cubic_curve_double_max_err
        self.current_point = None

    def move_to(self, point: tuple[float, float]):
        self.pen.moveTo(point)
        self.current_point = point

    def line_to(self, point: tuple[float, float]):
        self.pen.lineTo(point)
        self.current_point = point

    def cubic_curve_to(
            self,
            control_point_1: tuple[float, float],
            control_point_2: tuple[float, float],
            end_point: tuple[float, float],
    ):
        self.pen.qCurveTo(*cu2qu.curve_to_quadratic([self.current_point, control_point_1, control_point_2, end_point], self.cubic_curve_double_max_err)[1:])
        self.current_point = end_point

    def quadratic_curve_to(
            self,
            control_point: tuple[float, float],
            end_point: tuple[float, float],
    ):
        self.pen.qCurveTo(control_point, end_point)
        self.current_point = end_point

    def end_path(self):
        self.pen.endPath()
        self.current_point = None

    def close_path(self):
        self.pen.closePath()
        self.current_point = None

    def to_glyph(self) -> TtfGlyph:
        return self.pen.glyph()
