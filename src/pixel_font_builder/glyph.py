from typing import Any


class Glyph:
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
    ):
        self.name = name
        self.horizontal_offset_x, self.horizontal_offset_y = horizontal_offset
        self.advance_width = advance_width
        self.vertical_offset_x, self.vertical_offset_y = vertical_offset
        self.advance_height = advance_height
        self.bitmap = [] if bitmap is None else bitmap

    def __eq__(self, other: Any) -> bool:
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
    def horizontal_offset(self, value: tuple[int, int]):
        self.horizontal_offset_x, self.horizontal_offset_y = value

    @property
    def vertical_offset(self) -> tuple[int, int]:
        return self.vertical_offset_x, self.vertical_offset_y

    @vertical_offset.setter
    def vertical_offset(self, value: tuple[int, int]):
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

    def calculate_bitmap_left_padding(self) -> int:
        padding = 0
        for i in range(self.width):
            if any(bitmap_row[i] != 0 for bitmap_row in self.bitmap):
                break
            padding += 1
        return padding

    def calculate_bitmap_right_padding(self) -> int:
        padding = 0
        for i in range(self.width):
            if any(bitmap_row[-1 - i] != 0 for bitmap_row in self.bitmap):
                break
            padding += 1
        return padding

    def calculate_bitmap_top_padding(self) -> int:
        padding = 0
        for bitmap_row in self.bitmap:
            if any(color != 0 for color in bitmap_row):
                break
            padding += 1
        return padding

    def calculate_bitmap_bottom_padding(self) -> int:
        padding = 0
        for bitmap_row in reversed(self.bitmap):
            if any(color != 0 for color in bitmap_row):
                break
            padding += 1
        return padding
