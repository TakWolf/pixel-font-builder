from __future__ import annotations

from typing import Final, Any

from pixel_font_builder.opentype.feature import FeatureFile
from pixel_font_builder.opentype.outline import OutlinesPainter, SolidOutlinesPainter


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


class Config:
    DEFAULT_OUTLINES_PAINTER: Final = SolidOutlinesPainter()

    px_to_units: int
    has_vertical_metrics: bool
    head_bounding_box_override: BoundingBox | None
    outlines_painter: OutlinesPainter
    feature_files: list[FeatureFile]

    def __init__(
            self,
            px_to_units: int = 100,
            has_vertical_metrics: bool = True,
            head_bounding_box_override: BoundingBox | None = None,
            outlines_painter: OutlinesPainter | None = None,
            feature_files: list[FeatureFile] | None = None,
    ):
        self.px_to_units = px_to_units
        self.has_vertical_metrics = has_vertical_metrics
        self.head_bounding_box_override = head_bounding_box_override
        self.outlines_painter = Config.DEFAULT_OUTLINES_PAINTER if outlines_painter is None else outlines_painter
        self.feature_files = [] if feature_files is None else feature_files
