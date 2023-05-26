
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
