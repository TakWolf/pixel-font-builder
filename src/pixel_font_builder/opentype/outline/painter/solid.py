from __future__ import annotations

from pixel_font_builder.glyph import Glyph
from pixel_font_builder.opentype.outline.painter.base import OutlinesPainter
from pixel_font_builder.opentype.outline.pen.base import OutlinesPen


def _is_solid(bitmap: list[list[int]], x: int, y: int) -> bool:
    return 0 <= y < len(bitmap) and 0 <= x < len(bitmap[y]) and bitmap[y][x] != 0


def _is_collinear(point_1: tuple[int, int], point_2: tuple[int, int], point_3: tuple[int, int]) -> bool:
    return point_1[0] == point_2[0] == point_3[0] or point_1[1] == point_2[1] == point_3[1]


class SolidOutlinesPainter(OutlinesPainter):
    @staticmethod
    def create_pixel_outlines(bitmap: list[list[int]]) -> list[list[tuple[int, int]]]:
        edges = []
        pending_edges = set()
        for y, bitmap_row in enumerate(bitmap):
            for x, pixel in enumerate(bitmap_row):
                if pixel == 0:
                    continue

                if not _is_solid(bitmap, x, y - 1):
                    edge = (x, y), (x + 1, y)
                    edges.append(edge)
                    pending_edges.add(edge)

                if not _is_solid(bitmap, x + 1, y):
                    edge = (x + 1, y), (x + 1, y + 1)
                    edges.append(edge)
                    pending_edges.add(edge)

                if not _is_solid(bitmap, x, y + 1):
                    edge = (x + 1, y + 1), (x, y + 1)
                    edges.append(edge)
                    pending_edges.add(edge)

                if not _is_solid(bitmap, x - 1, y):
                    edge = (x, y + 1), (x, y)
                    edges.append(edge)
                    pending_edges.add(edge)

        outlines = []
        for start_point, current_point in edges:
            if (start_point, current_point) not in pending_edges:
                continue
            pending_edges.remove((start_point, current_point))
            outline = [start_point, current_point]

            dx = current_point[0] - start_point[0]
            dy = current_point[1] - start_point[1]

            while current_point != start_point:
                x, y = current_point
                for next_dx, next_dy in ((-dy, dx), (dx, dy), (dy, -dx), (-dx, -dy)):
                    next_point = x + next_dx, y + next_dy
                    edge = current_point, next_point
                    if edge in pending_edges:
                        pending_edges.remove(edge)

                        if len(outline) >= 2 and _is_collinear(outline[-2], outline[-1], next_point):
                            outline[-1] = next_point
                        else:
                            outline.append(next_point)

                        current_point = next_point
                        dx, dy = next_dx, next_dy
                        break
                else:
                    raise AssertionError()

            outline.pop()
            if _is_collinear(outline[-1], outline[0], outline[1]):
                outline.pop(0)
            outlines.append(outline)
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
