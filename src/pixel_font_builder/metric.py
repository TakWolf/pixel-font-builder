from __future__ import annotations

from typing import Any


class LineMetric:
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

    def __mul__(self, other: Any) -> LineMetric:
        if not isinstance(other, int):
            raise TypeError(f"can't multiply 'LineMetric' by non-int of type '{type(other).__name__}'")
        return LineMetric(
            self.ascent * other,
            self.descent * other,
            self.line_gap * other,
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, LineMetric):
            return NotImplemented
        return (self.ascent == other.ascent and
                self.descent == other.descent and
                self.line_gap == other.line_gap)

    @property
    def line_height(self) -> int:
        return self.ascent - self.descent


class FontMetric:
    font_size: int
    horizontal_layout: LineMetric
    vertical_layout: LineMetric
    x_height: int
    cap_height: int
    underline_position: int
    underline_thickness: int
    strikeout_position: int
    strikeout_thickness: int

    def __init__(
            self,
            font_size: int = 0,
            horizontal_layout: LineMetric | None = None,
            vertical_layout: LineMetric | None = None,
            x_height: int = 0,
            cap_height: int = 0,
            underline_position: int = 0,
            underline_thickness: int = 0,
            strikeout_position: int = 0,
            strikeout_thickness: int = 0,
    ):
        self.font_size = font_size
        self.horizontal_layout = LineMetric() if horizontal_layout is None else horizontal_layout
        self.vertical_layout = LineMetric() if vertical_layout is None else vertical_layout
        self.x_height = x_height
        self.cap_height = cap_height
        self.underline_position = underline_position
        self.underline_thickness = underline_thickness
        self.strikeout_position = strikeout_position
        self.strikeout_thickness = strikeout_thickness

    def __mul__(self, other: Any) -> FontMetric:
        if not isinstance(other, int):
            raise TypeError(f"can't multiply 'FontMetric' by non-int of type '{type(other).__name__}'")
        return FontMetric(
            self.font_size * other,
            self.horizontal_layout * other,
            self.vertical_layout * other,
            self.x_height * other,
            self.cap_height * other,
            self.underline_position * other,
            self.underline_thickness * other,
            self.strikeout_position * other,
            self.strikeout_thickness * other,
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, FontMetric):
            return NotImplemented
        return (self.font_size == other.font_size and
                self.horizontal_layout == other.horizontal_layout and
                self.vertical_layout == other.vertical_layout and
                self.x_height == other.x_height and
                self.cap_height == other.cap_height and
                self.underline_position == other.underline_position and
                self.underline_thickness == other.underline_thickness and
                self.strikeout_position == other.strikeout_position and
                self.strikeout_thickness == other.strikeout_thickness)
