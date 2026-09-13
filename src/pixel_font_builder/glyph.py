from __future__ import annotations

from typing import Any


class Glyph:
    """A glyph bitmap and its horizontal and vertical layout metrics.

    The bitmap uses image coordinates: rows run from top to bottom and columns
    run from left to right. Each matrix element represents one pixel, and all
    offsets and advances are expressed in the same pixel-grid units.

    ``horizontal_offset`` is the position of the bitmap bounding box's
    bottom-left corner relative to the horizontal writing origin. Its x value
    is positive to the right, and its y value is positive upward from the
    baseline. The bitmap therefore occupies
    ``[offset_x, offset_x + width]`` horizontally and
    ``[offset_y, offset_y + height]`` vertically. ``advance_width`` is the
    distance to the next horizontal writing origin.

    ``vertical_offset`` is the position of the bitmap bounding box's top-left
    corner relative to the vertical writing origin, following the OpenType
    vertical bitmap-bearing convention. Its x value is positive to the right,
    and its y value is positive downward in the vertical writing direction.
    ``advance_height`` is the distance to the next vertical writing origin in
    that direction.

    Offsets position the complete bitmap; they do not remove transparent rows
    or columns. Padding inside the bitmap remains part of its dimensions.
    """

    name: str
    horizontal_offset_x: int
    horizontal_offset_y: int
    advance_width: int
    vertical_offset_x: int
    vertical_offset_y: int
    advance_height: int
    bitmap: list[list[int]]

    def __init__(
            self,
            name: str,
            horizontal_offset: tuple[int, int] = (0, 0),
            advance_width: int = 0,
            vertical_offset: tuple[int, int] = (0, 0),
            advance_height: int = 0,
            bitmap: list[list[int]] | None = None,
    ) -> None:
        self.name = name
        self.horizontal_offset_x, self.horizontal_offset_y = horizontal_offset
        self.advance_width = advance_width
        self.vertical_offset_x, self.vertical_offset_y = vertical_offset
        self.advance_height = advance_height
        self.bitmap = bitmap if bitmap is not None else []

    def __copy__(self) -> Glyph:
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any]) -> Glyph:
        return self.deepcopy()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Glyph):
            return NotImplemented
        return (self.name == other.name and
                self.horizontal_offset_x == other.horizontal_offset_x and
                self.horizontal_offset_y == other.horizontal_offset_y and
                self.advance_width == other.advance_width and
                self.vertical_offset_x == other.vertical_offset_x and
                self.vertical_offset_y == other.vertical_offset_y and
                self.advance_height == other.advance_height and
                self.bitmap == other.bitmap)

    @property
    def horizontal_offset(self) -> tuple[int, int]:
        return self.horizontal_offset_x, self.horizontal_offset_y

    @horizontal_offset.setter
    def horizontal_offset(self, value: tuple[int, int]) -> None:
        self.horizontal_offset_x, self.horizontal_offset_y = value

    @property
    def vertical_offset(self) -> tuple[int, int]:
        return self.vertical_offset_x, self.vertical_offset_y

    @vertical_offset.setter
    def vertical_offset(self, value: tuple[int, int]) -> None:
        self.vertical_offset_x, self.vertical_offset_y = value

    @property
    def width(self) -> int:
        if len(self.bitmap) > 0:
            return len(self.bitmap[0])
        else:
            return 0

    @property
    def height(self) -> int:
        return len(self.bitmap)

    @property
    def dimensions(self) -> tuple[int, int]:
        return self.width, self.height

    def copy(self) -> Glyph:
        return Glyph(
            self.name,
            self.horizontal_offset,
            self.advance_width,
            self.vertical_offset,
            self.advance_height,
            self.bitmap,
        )

    def deepcopy(self) -> Glyph:
        return Glyph(
            self.name,
            self.horizontal_offset,
            self.advance_width,
            self.vertical_offset,
            self.advance_height,
            [bitmap_row.copy() for bitmap_row in self.bitmap],
        )
