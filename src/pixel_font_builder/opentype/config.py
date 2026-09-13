from __future__ import annotations

from typing import Any, Final

from pixel_font_builder.opentype.feature.source.base import FeatureSource
from pixel_font_builder.opentype.outline.painter.base import OutlinesPainter
from pixel_font_builder.opentype.outline.painter.solid import SolidOutlinesPainter


class FieldsOverride:
    head_x_min: int | None
    head_y_min: int | None
    head_x_max: int | None
    head_y_max: int | None
    os2_x_avg_char_width: int | None

    def __init__(
            self,
            head_x_min: int | None = None,
            head_y_min: int | None = None,
            head_x_max: int | None = None,
            head_y_max: int | None = None,
            os2_x_avg_char_width: int | None = None,
    ) -> None:
        self.head_x_min = head_x_min
        self.head_y_min = head_y_min
        self.head_x_max = head_x_max
        self.head_y_max = head_y_max
        self.os2_x_avg_char_width = os2_x_avg_char_width

    def __copy__(self) -> FieldsOverride:
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any]) -> FieldsOverride:
        return self.deepcopy()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FieldsOverride):
            return NotImplemented
        return (self.head_x_min == other.head_x_min and
                self.head_y_min == other.head_y_min and
                self.head_x_max == other.head_x_max and
                self.head_y_max == other.head_y_max and
                self.os2_x_avg_char_width == other.os2_x_avg_char_width)

    def copy(self) -> FieldsOverride:
        return FieldsOverride(
            self.head_x_min,
            self.head_y_min,
            self.head_x_max,
            self.head_y_max,
            self.os2_x_avg_char_width,
        )

    def deepcopy(self) -> FieldsOverride:
        return self.copy()


class Config:
    DEFAULT_OUTLINES_PAINTER: Final = SolidOutlinesPainter()

    px_to_units: int
    outlines_painter: OutlinesPainter
    has_vertical_metrics: bool
    fields_override: FieldsOverride
    features: FeatureSource | None

    def __init__(
            self,
            px_to_units: int = 100,
            outlines_painter: OutlinesPainter | None = None,
            has_vertical_metrics: bool = True,
            fields_override: FieldsOverride | None = None,
            features: FeatureSource | None = None,
    ) -> None:
        self.px_to_units = px_to_units
        self.outlines_painter = outlines_painter if outlines_painter is not None else Config.DEFAULT_OUTLINES_PAINTER
        self.has_vertical_metrics = has_vertical_metrics
        self.fields_override = fields_override if fields_override is not None else FieldsOverride()
        self.features = features

    def __copy__(self) -> Config:
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any]) -> Config:
        return self.deepcopy()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Config):
            return NotImplemented
        return (self.px_to_units == other.px_to_units and
                self.outlines_painter == other.outlines_painter and
                self.has_vertical_metrics == other.has_vertical_metrics and
                self.fields_override == other.fields_override and
                self.features == other.features)

    def copy(self) -> Config:
        return Config(
            self.px_to_units,
            self.outlines_painter,
            self.has_vertical_metrics,
            self.fields_override,
            self.features,
        )

    def deepcopy(self) -> Config:
        return Config(
            self.px_to_units,
            self.outlines_painter.deepcopy(),
            self.has_vertical_metrics,
            self.fields_override.deepcopy(),
            self.features.deepcopy() if self.features is not None else None,
        )
