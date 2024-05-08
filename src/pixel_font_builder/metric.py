
class FontLayoutHeader:
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

    def __mul__(self, other: int) -> 'FontLayoutHeader':
        return FontLayoutHeader(
            self.ascent * other,
            self.descent * other,
            self.line_gap * other,
        )


class FontMetrics:
    def __init__(
            self,
            font_size: int = 0,
            horizontal_layout: FontLayoutHeader = None,
            vertical_layout: FontLayoutHeader = None,
            x_height: int = 0,
            cap_height: int = 0,
    ):
        self.font_size = font_size
        if horizontal_layout is None:
            horizontal_layout = FontLayoutHeader()
        self.horizontal_layout = horizontal_layout
        if vertical_layout is None:
            vertical_layout = FontLayoutHeader()
        self.vertical_layout = vertical_layout
        self.x_height = x_height
        self.cap_height = cap_height

    def __mul__(self, other: int) -> 'FontMetrics':
        return FontMetrics(
            self.font_size * other,
            self.horizontal_layout * other,
            self.vertical_layout * other,
            self.x_height * other,
            self.cap_height * other,
        )
