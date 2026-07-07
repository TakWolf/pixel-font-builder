from __future__ import annotations

from pixel_font_builder.glyph import Glyph
from pixel_font_builder.opentype.outline.painter.base import OutlinesPainter
from pixel_font_builder.opentype.outline.pen.base import OutlinesPen


class SolidOutlinesPainter(OutlinesPainter):
    @staticmethod
    def create_pixel_outlines(bitmap: list[list[int]]) -> list[list[tuple[int, int]]]:
        # 相邻像素分组
        point_groups = []
        for y, bitmap_row in enumerate(bitmap):
            for x, pixel in enumerate(bitmap_row):
                if pixel == 0:
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
                if x <= 0 or bitmap[y][x - 1] == 0:  # 左
                    pending_segments.append([point_outline[3], point_outline[0]])
                if x >= len(bitmap[y]) - 1 or bitmap[y][x + 1] == 0:  # 右
                    pending_segments.append([point_outline[1], point_outline[2]])
                if y <= 0 or bitmap[y - 1][x] == 0:  # 上
                    pending_segments.append([point_outline[0], point_outline[1]])
                if y >= len(bitmap) - 1 or bitmap[y + 1][x] == 0:  # 下
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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SolidOutlinesPainter):
            return NotImplemented
        return True

    def draw_outlines(self, glyph: Glyph, pen: OutlinesPen, px_to_units: int):
        outlines = SolidOutlinesPainter.create_pixel_outlines(glyph.bitmap)
        for outline in outlines:
            for index, (x, y) in enumerate(outline):
                x = (x + glyph.horizontal_offset_x) * px_to_units
                y = (glyph.height + glyph.horizontal_offset_y - y) * px_to_units

                if index == 0:
                    pen.move_to((x, y))
                else:
                    pen.line_to((x, y))
            pen.close_path()

    def copy(self) -> SolidOutlinesPainter:
        return self

    def deepcopy(self) -> SolidOutlinesPainter:
        return self.copy()
