from __future__ import annotations

from typing import Any


class BoundingBox:
    x_min: int
    y_min: int
    x_max: int
    y_max: int

    def __init__(
            self,
            x_min: int = 0,
            y_min: int = 0,
            x_max: int = 0,
            y_max: int = 0,
    ):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max

    @property
    def width(self) -> int:
        return self.x_max - self.x_min

    @property
    def height(self) -> int:
        return self.y_max - self.y_min

    def __mul__(self, other: Any) -> BoundingBox:
        if not isinstance(other, int):
            raise TypeError(f"can't multiply 'BoundingBox' by non-int of type '{type(other).__name__}'")
        return BoundingBox(
            self.x_min * other,
            self.y_min * other,
            self.x_max * other,
            self.y_max * other,
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, BoundingBox):
            return NotImplemented
        return (self.x_min == other.x_min and
                self.y_min == other.y_min and
                self.x_max == other.x_max and
                self.y_max == other.y_max)
