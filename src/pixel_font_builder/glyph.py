
class Glyph:
    def __init__(
            self,
            name: str,
            advance_width: int = 0,
            offset: tuple[int, int] = (0, 0),
            data: list[list[int]] = None,
    ):
        self.name = name
        self.advance_width = advance_width
        self.offset = offset
        if data is None:
            data = []
        self.data = data

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
    def size(self) -> tuple[int, int]:
        return self.width, self.height
