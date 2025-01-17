from typing import Any


class FontLayoutHeader:
    ascent: int
    descent: int
    line_gap: int

    def __init__(
            self,
            ascent: int = 0,
            descent: int = 0,
            line_gap: int = 0,
    ):
        self.ascent = ascent
        self.descent = descent
        self.line_gap = line_gap

    @property
    def line_height(self) -> int:
        return self.ascent - self.descent

    def __mul__(self, other: Any) -> 'FontLayoutHeader':
        if not isinstance(other, int):
            raise TypeError(f"can't multiply 'FontLayoutHeader' by non-int of type '{type(other).__name__}'")
        return FontLayoutHeader(
            self.ascent * other,
            self.descent * other,
            self.line_gap * other,
        )


class FontMetric:
    font_size: int
    horizontal_layout: FontLayoutHeader
    vertical_layout: FontLayoutHeader
    x_height: int
    cap_height: int

    def __init__(
            self,
            font_size: int = 0,
            horizontal_layout: FontLayoutHeader | None = None,
            vertical_layout: FontLayoutHeader | None = None,
            x_height: int = 0,
            cap_height: int = 0,
    ):
        self.font_size = font_size
        self.horizontal_layout = FontLayoutHeader() if horizontal_layout is None else horizontal_layout
        self.vertical_layout = FontLayoutHeader() if vertical_layout is None else vertical_layout
        self.x_height = x_height
        self.cap_height = cap_height

    def __mul__(self, other: Any) -> 'FontMetric':
        if not isinstance(other, int):
            raise TypeError(f"can't multiply 'FontMetric' by non-int of type '{type(other).__name__}'")
        return FontMetric(
            self.font_size * other,
            self.horizontal_layout * other,
            self.vertical_layout * other,
            self.x_height * other,
            self.cap_height * other,
        )
