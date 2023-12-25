
class Glyph:
    def __init__(
            self,
            name: str,
            advance_width: int = 0,
            advance_height: int = 0,
            horizontal_origin: tuple[int, int] = (0, 0),
            vertical_origin_y: int = 0,
            data: list[list[int]] = None,
    ):
        self.name = name
        self.advance_width = advance_width
        self.advance_height = advance_height
        self.horizontal_origin_x, self.horizontal_origin_y = horizontal_origin
        self.vertical_origin_y = vertical_origin_y
        if data is None:
            data = []
        self.data = data

    @property
    def horizontal_origin(self) -> tuple[int, int]:
        return self.horizontal_origin_x, self.horizontal_origin_y

    @horizontal_origin.setter
    def horizontal_origin(self, value: tuple[int, int]):
        self.horizontal_origin_x, self.horizontal_origin_y = value

    @property
    def width(self) -> int:
        if len(self.data) > 0:
            return len(self.data[0])
        else:
            return 0

    @property
    def height(self) -> int:
        return len(self.data)

    @property
    def dimensions(self) -> tuple[int, int]:
        return self.width, self.height

    def calculate_top_side_bearing(self) -> int:
        top_empty = 0
        for data_row in self.data:
            if any(data_row) != 0:
                break
            top_empty += 1
        return top_empty - self.vertical_origin_y

    def check_ready(self):
        if any(len(data_row) != len(self.data[0]) for data_row in self.data):
            raise Exception(f"Glyph '{self.name}': lengths of data rows are not equals")
