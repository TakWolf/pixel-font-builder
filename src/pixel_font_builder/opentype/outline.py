import math
from abc import abstractmethod
from typing import Protocol, runtime_checkable

from fontTools import cu2qu
from fontTools.misc.psCharStrings import T2CharString as OtfGlyph
from fontTools.pens.t2CharStringPen import T2CharStringPen as OtfGlyphPen
from fontTools.pens.ttGlyphPen import TTGlyphPen as TtfGlyphPen
# noinspection PyProtectedMember
from fontTools.ttLib.tables._g_l_y_f import Glyph as TtfGlyph

from pixel_font_builder.glyph import Glyph

type XtfGlyph = OtfGlyph | TtfGlyph


class OutlinesPen:
    is_ttf: bool
    pen: OtfGlyphPen | TtfGlyphPen
    current_point: tuple[float, float] | None

    def __init__(
            self,
            is_ttf: bool,
            advance_width: int,
    ):
        self.is_ttf = is_ttf
        self.pen = TtfGlyphPen() if is_ttf else OtfGlyphPen(advance_width, None)
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
            double_max_err: float = 1,
    ):
        if self.is_ttf:
            self.pen.qCurveTo(*cu2qu.curve_to_quadratic([self.current_point, control_point_1, control_point_2, end_point], double_max_err)[1:])
        else:
            self.pen.curveTo(control_point_1, control_point_2, end_point)
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

    def to_glyph(self) -> XtfGlyph:
        return self.pen.glyph() if self.is_ttf else self.pen.getCharString()


@runtime_checkable
class OutlinesPainter(Protocol):
    @abstractmethod
    def draw_outlines(self, glyph: Glyph, pen: OutlinesPen, px_to_units: int):
        raise NotImplementedError()


class SolidOutlinesPainter(OutlinesPainter):
    @staticmethod
    def _create_outlines(bitmap: list[list[int]]) -> list[list[tuple[int, int]]]:
        # 相邻像素分组
        point_groups = []
        for y, bitmap_row in enumerate(bitmap):
            for x, color in enumerate(bitmap_row):
                if color == 0:
                    continue

                new_point_group = {(x, y)}
                for point_group in reversed(point_groups):
                    # 遍历方向为右下，因此只需检查左上
                    if (x - 1, y) in point_group or (x, y - 1) in point_group:
                        point_groups.remove(point_group)
                        new_point_group.update(point_group)
                point_groups.append(new_point_group)

        # 每组生成轮廓
        outlines = []
        for point_group in point_groups:
            # 按照像素拆分线段，注意绘制顺序
            pending_segments = []
            for x, y in point_group:
                # 一个像素有左右上下四条边，如果该边没有相邻像素，则该边线段有效
                point_outline = [(x, y), (x + 1, y), (x + 1, y + 1), (x, y + 1)]
                if x <= 0 or bitmap[y][x - 1] <= 0:  # 左
                    pending_segments.append([point_outline[3], point_outline[0]])
                if x >= len(bitmap[y]) - 1 or bitmap[y][x + 1] <= 0:  # 右
                    pending_segments.append([point_outline[1], point_outline[2]])
                if y <= 0 or bitmap[y - 1][x] <= 0:  # 上
                    pending_segments.append([point_outline[0], point_outline[1]])
                if y >= len(bitmap) - 1 or bitmap[y + 1][x] <= 0:  # 下
                    pending_segments.append([point_outline[2], point_outline[3]])

            # 连接所有的线段，注意绘制顺序
            solved_segments = []
            while len(pending_segments) > 0:
                pending_segment = pending_segments.pop()
                for solved_segment in reversed(solved_segments):
                    # 一共四种连接情况
                    left_segment = None
                    right_segment = None
                    if pending_segment[-1] == solved_segment[0]:
                        left_segment = pending_segment
                        right_segment = solved_segment
                    elif pending_segment[-1] == solved_segment[-1]:
                        solved_segment.reverse()
                        left_segment = pending_segment
                        right_segment = solved_segment
                    elif solved_segment[-1] == pending_segment[0]:
                        left_segment = solved_segment
                        right_segment = pending_segment
                    elif solved_segment[-1] == pending_segment[-1]:
                        pending_segment.reverse()
                        left_segment = solved_segment
                        right_segment = pending_segment

                    # 需要连接的情况
                    if left_segment is not None and right_segment is not None:
                        solved_segments.remove(solved_segment)

                        # 连接的两个点是重复的
                        right_segment.pop(0)

                        # 判断连接的点是不是可省略
                        x, y = left_segment[-1]
                        xl, yl = left_segment[-2]
                        xr, yr = right_segment[0]
                        if (x == xl and x == xr) or (y == yl and y == yr):
                            left_segment.pop()

                        pending_segment = left_segment + right_segment
                solved_segments.append(pending_segment)

            # 将连接好的线段添加到轮廓数组中，有多条线段的情况，是中间有镂空（绘制顺序与外边框相反）
            for solved_segment in solved_segments:
                # 首尾的两个点是重复的
                solved_segment.pop(0)

                # 判断尾点是不是可省略
                x, y = solved_segment[-1]
                xl, yl = solved_segment[-2]
                xr, yr = solved_segment[0]
                if (x == xl and x == xr) or (y == yl and y == yr):
                    solved_segment.pop()

                outlines.append(solved_segment)
        return outlines

    def draw_outlines(self, glyph: Glyph, pen: OutlinesPen, px_to_units: int):
        outlines = self._create_outlines(glyph.bitmap)
        for outline in outlines:
            for index, (x, y) in enumerate(outline):
                x = (x + glyph.horizontal_offset_x) * px_to_units
                y = (glyph.height + glyph.horizontal_offset_y - y) * px_to_units

                if index == 0:
                    pen.move_to((x, y))
                else:
                    pen.line_to((x, y))
            pen.close_path()


class SquareDotOutlinesPainter(OutlinesPainter):
    size: float

    def __init__(self, size: float = 0.8):
        self.size = size

    def draw_outlines(self, glyph: Glyph, pen: OutlinesPen, px_to_units: int):
        size = self.size * px_to_units
        offset = (1 - self.size) / 2 * px_to_units
        for y, bitmap_row in enumerate(glyph.bitmap):
            y = (glyph.height + glyph.horizontal_offset_y - y) * px_to_units - offset
            for x, color in enumerate(bitmap_row):
                x = (x + glyph.horizontal_offset_x) * px_to_units + offset
                if color != 0:
                    pen.move_to((x, y))
                    pen.line_to((x + size, y))
                    pen.line_to((x + size, y - size))
                    pen.line_to((x, y - size))
                    pen.close_path()


class CircleDotOutlinesPainter(OutlinesPainter):
    radius: float

    def __init__(self, radius: float = 0.4):
        self.radius = radius

    def draw_outlines(self, glyph: Glyph, pen: OutlinesPen, px_to_units: int):
        radius = self.radius * px_to_units
        c = radius * 4 / 3 * (math.sqrt(2) - 1)
        for y, bitmap_row in enumerate(glyph.bitmap):
            y = (glyph.height + glyph.horizontal_offset_y - y - 0.5) * px_to_units
            for x, color in enumerate(bitmap_row):
                x = (x + glyph.horizontal_offset_x + 0.5) * px_to_units
                if color != 0:
                    pen.move_to((x, y + radius))
                    pen.cubic_curve_to((x + c, y + radius), (x + radius, y + c), (x + radius, y))
                    pen.cubic_curve_to((x + radius, y - c), (x + c, y - radius), (x, y - radius))
                    pen.cubic_curve_to((x - c, y - radius), (x - radius, y - c), (x - radius, y))
                    pen.cubic_curve_to((x - radius, y + c), (x - c, y + radius), (x, y + radius))
                    pen.close_path()


def create_xtf_glyphs(
        is_ttf: bool,
        outlines_painter: OutlinesPainter,
        name_to_glyph: dict[str, Glyph],
        px_to_units: int,
) -> tuple[dict[str, XtfGlyph], dict[str, tuple[int, int]], dict[str, tuple[int, int]]]:
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

        pen = OutlinesPen(is_ttf, advance_width)
        outlines_painter.draw_outlines(glyph, pen, px_to_units)
        xtf_glyphs[glyph_name] = pen.to_glyph()
    return xtf_glyphs, horizontal_metrics, vertical_metrics
