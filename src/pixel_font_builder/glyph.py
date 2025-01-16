
class Glyph:
    name: str
    horizontal_origin_x: int
    horizontal_origin_y: int
    advance_width: int
    vertical_origin_x: int
    vertical_origin_y: int
    advance_height: int
    bitmap: list[list[int]]

    def __init__(
            self,
            name: str,
            horizontal_origin: tuple[int, int] = (0, 0),
            advance_width: int = 0,
            vertical_origin: tuple[int, int] = (0, 0),
            advance_height: int = 0,
            bitmap: list[list[int]] | None = None,
    ):
        self.name = name
        self.horizontal_origin_x, self.horizontal_origin_y = horizontal_origin
        self.advance_width = advance_width
        self.vertical_origin_x, self.vertical_origin_y = vertical_origin
        self.advance_height = advance_height
        self.bitmap = [] if bitmap is None else bitmap

    @property
    def horizontal_origin(self) -> tuple[int, int]:
        return self.horizontal_origin_x, self.horizontal_origin_y

    @horizontal_origin.setter
    def horizontal_origin(self, value: tuple[int, int]):
        self.horizontal_origin_x, self.horizontal_origin_y = value

    @property
    def vertical_origin(self) -> tuple[int, int]:
        return self.vertical_origin_x, self.vertical_origin_y

    @vertical_origin.setter
    def vertical_origin(self, value: tuple[int, int]):
        self.vertical_origin_x, self.vertical_origin_y = value

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
            if any(bitmap_row[i] for bitmap_row in self.bitmap) != 0:
                break
            padding += 1
        return padding

    def calculate_bitmap_right_padding(self) -> int:
        padding = 0
        for i in range(self.width):
            if any(bitmap_row[-1 - i] for bitmap_row in self.bitmap) != 0:
                break
            padding += 1
        return padding

    def calculate_bitmap_top_padding(self) -> int:
        padding = 0
        for bitmap_row in self.bitmap:
            if any(bitmap_row) != 0:
                break
            padding += 1
        return padding

    def calculate_bitmap_bottom_padding(self) -> int:
        padding = 0
        for bitmap_row in reversed(self.bitmap):
            if any(bitmap_row) != 0:
                break
            padding += 1
        return padding
