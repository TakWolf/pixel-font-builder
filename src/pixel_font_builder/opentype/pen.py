from abc import abstractmethod
from typing import Protocol, runtime_checkable

from fontTools.misc.psCharStrings import T2CharString as OTFGlyph
from fontTools.pens.t2CharStringPen import T2CharStringPen as OTFGlyphPen
from fontTools.pens.ttGlyphPen import TTGlyphPen as TTFGlyphPen
# noinspection PyProtectedMember
from fontTools.ttLib.tables._g_l_y_f import Glyph as TTFGlyph

from pixel_font_builder.glyph import Glyph

type XTFGlyph = OTFGlyph | TTFGlyph


class OutlinesPen:
    is_ttf: bool
    pen: OTFGlyphPen | TTFGlyphPen

    def __init__(self, is_ttf: bool, advance_width: int):
        self.is_ttf = is_ttf
        self.pen = TTFGlyphPen() if is_ttf else OTFGlyphPen(advance_width, None)

    def move_to(self, point: tuple[float, float]):
        self.pen.moveTo(point)

    def line_to(self, point: tuple[float, float]):
        self.pen.lineTo(point)

    def curve_to(self, *points: tuple[float, float]):
        self.pen.curveTo(*points)

    def q_curve_to(self, *points: tuple[float, float]):
        self.pen.qCurveTo(*points)

    def end_path(self):
        self.pen.endPath()

    def close_path(self):
        self.pen.closePath()

    def to_glyph(self) -> XTFGlyph:
        return self.pen.glyph() if self.is_ttf else self.pen.getCharString()


@runtime_checkable
class OutlinesPainter(Protocol):
    @abstractmethod
    def draw_outlines(self, glyph: Glyph, pen: OutlinesPen, px_to_units: int):
        raise NotImplementedError


class SolidOutlinesPainter(OutlinesPainter):
    @staticmethod
    def _create_outlines(bitmap: list[list[int]]) -> list[list[tuple[int, int]]]:
        # 相邻像素分组
        point_group_list = []
        for y, bitmap_row in enumerate(bitmap):
            for x, color in enumerate(bitmap_row):
                if color != 0:
                    new_point_group = {(x, y)}
                    for i, point_group in enumerate(reversed(point_group_list)):
                        # 遍历方向为右下，因此只需检查左上
                        if (x - 1, y) in point_group or (x, y - 1) in point_group:
                            point_group_list.remove(point_group)
                            new_point_group = new_point_group.union(point_group)
                    point_group_list.append(new_point_group)
        # 对每组生成轮廓
        outlines = []
        for point_group in point_group_list:
            # 按照像素拆分线段，注意绘制顺序
            pending_line_segments = []
            for (x, y) in point_group:
                point_outline = [(x, y), (x + 1, y), (x + 1, y + 1), (x, y + 1)]
                # 一个像素有左右上下四条边，如果该边没有相邻像素，则该边线段有效
                if x <= 0 or bitmap[y][x - 1] <= 0:  # 左
                    pending_line_segments.append([point_outline[3], point_outline[0]])
                if x >= len(bitmap[y]) - 1 or bitmap[y][x + 1] <= 0:  # 右
                    pending_line_segments.append([point_outline[1], point_outline[2]])
                if y <= 0 or bitmap[y - 1][x] <= 0:  # 上
                    pending_line_segments.append([point_outline[0], point_outline[1]])
                if y >= len(bitmap) - 1 or bitmap[y + 1][x] <= 0:  # 下
                    pending_line_segments.append([point_outline[2], point_outline[3]])
            # 连接所有的线段，注意绘制顺序
            solved_line_segments = []
            while len(pending_line_segments) > 0:
                pending_line_segment = pending_line_segments.pop()
                for i, solved_line_segment in enumerate(reversed(solved_line_segments)):
                    left_line_segment = None
                    right_line_segment = None
                    # 一共4种连接情况
                    if pending_line_segment[-1] == solved_line_segment[0]:
                        left_line_segment = pending_line_segment
                        right_line_segment = solved_line_segment
                    elif pending_line_segment[-1] == solved_line_segment[-1]:
                        solved_line_segment.reverse()
                        left_line_segment = pending_line_segment
                        right_line_segment = solved_line_segment
                    elif solved_line_segment[-1] == pending_line_segment[0]:
                        left_line_segment = solved_line_segment
                        right_line_segment = pending_line_segment
                    elif solved_line_segment[-1] == pending_line_segment[-1]:
                        pending_line_segment.reverse()
                        left_line_segment = solved_line_segment
                        right_line_segment = pending_line_segment
                    # 需要连接的情况
                    if left_line_segment is not None and right_line_segment is not None:
                        solved_line_segments.remove(solved_line_segment)
                        # 连接的两个点是重复的
                        right_line_segment.pop(0)
                        # 判断连接的点是不是可省略
                        x, y = left_line_segment[-1]
                        xl, yl = left_line_segment[-2]
                        xr, yr = right_line_segment[0]
                        if (x == xl and x == xr) or (y == yl and y == yr):
                            left_line_segment.pop()
                        # 连接线段
                        pending_line_segment = left_line_segment + right_line_segment
                solved_line_segments.append(pending_line_segment)
            # 将连接好的线段添加到轮廓数组中，有多条线段的情况，是中间有镂空（绘制顺序与外边框相反）
            for solved_line_segment in solved_line_segments:
                # 首尾的两个点是重复的
                solved_line_segment.pop(0)
                # 判断尾点是不是可省略
                x, y = solved_line_segment[-1]
                xl, yl = solved_line_segment[-2]
                xr, yr = solved_line_segment[0]
                if (x == xl and x == xr) or (y == yl and y == yr):
                    solved_line_segment.pop()
                # 添加到轮廓
                outlines.append(solved_line_segment)
        return outlines

    def draw_outlines(self, glyph: Glyph, pen: OutlinesPen, px_to_units: int):
        outlines = self._create_outlines(glyph.bitmap)
        for outline in outlines:
            for index, (x, y) in enumerate(outline):
                x = (x + glyph.horizontal_origin_x) * px_to_units
                y = (glyph.height + glyph.horizontal_origin_y - y) * px_to_units

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
        for y, bitmap_row in enumerate(glyph.bitmap):
            y = (glyph.height + glyph.horizontal_origin_y - y) * px_to_units
            for x, color in enumerate(bitmap_row):
                x = (x + glyph.horizontal_origin_x) * px_to_units
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
        for y, bitmap_row in enumerate(glyph.bitmap):
            y = (glyph.height + glyph.horizontal_origin_y - y - 0.5) * px_to_units
            for x, color in enumerate(bitmap_row):
                x = (x + glyph.horizontal_origin_x + 0.5) * px_to_units
                if color != 0:
                    pen.move_to((x, y + radius))
                    pen.q_curve_to((x + radius, y + radius), (x + radius, y))
                    pen.q_curve_to((x + radius, y - radius), (x, y - radius))
                    pen.q_curve_to((x - radius, y - radius), (x - radius, y))
                    pen.q_curve_to((x - radius, y + radius), (x, y + radius))
                    pen.close_path()
