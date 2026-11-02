from __future__ import annotations

from enum import StrEnum, unique
from typing import Any, Final

from pixel_font_builder.opentype.feature.source.source import FeatureSource
from pixel_font_builder.opentype.outline.painter.painter import OutlinePainter
from pixel_font_builder.opentype.outline.painter.solid import SolidOutlinePainter


class FieldOverrides:
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

    def __copy__(self) -> FieldOverrides:
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any]) -> FieldOverrides:
        return self.deepcopy()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FieldOverrides):
            return NotImplemented
        return (self.head_x_min == other.head_x_min and
                self.head_y_min == other.head_y_min and
                self.head_x_max == other.head_x_max and
                self.head_y_max == other.head_y_max and
                self.os2_x_avg_char_width == other.os2_x_avg_char_width)

    def copy(self) -> FieldOverrides:
        return FieldOverrides(
            self.head_x_min,
            self.head_y_min,
            self.head_x_max,
            self.head_y_max,
            self.os2_x_avg_char_width,
        )

    def deepcopy(self) -> FieldOverrides:
        return self.copy()


@unique
class UserKerningMode(StrEnum):
    # Let any user kern feature or variation block take over all kerning.
    # Skip all generated kerning when such a block exists, even if it is empty
    # or limited to particular glyph pairs, scripts, languages, or conditions.
    # Generate kerning normally when no user kern block exists.
    TAKEOVER = 'Takeover'

    # Prepend generated kerning while preserving all user feature statements.
    # Rules are not deduplicated or merged by glyph pair. When both sets of rules
    # apply to the same pair, their positioning adjustments can accumulate.
    # Generated kerning uses DFLT/dflt; user script and language declarations
    # still determine where user rules apply.
    COEXIST = 'Coexist'


class Config:
    DEFAULT_OUTLINE_PAINTER: Final = SolidOutlinePainter()

    px_to_units: int
    outline_painter: OutlinePainter
    has_vertical_metrics: bool
    is_fixed_pitch: bool
    field_overrides: FieldOverrides
    user_kerning_mode: UserKerningMode
    features: FeatureSource | None

    def __init__(
            self,
            px_to_units: int = 100,
            outline_painter: OutlinePainter | None = None,
            has_vertical_metrics: bool = True,
            is_fixed_pitch: bool = False,
            field_overrides: FieldOverrides | None = None,
            user_kerning_mode: UserKerningMode = UserKerningMode.TAKEOVER,
            features: FeatureSource | None = None,
    ) -> None:
        self.px_to_units = px_to_units
        self.outline_painter = outline_painter if outline_painter is not None else Config.DEFAULT_OUTLINE_PAINTER
        self.has_vertical_metrics = has_vertical_metrics
        self.is_fixed_pitch = is_fixed_pitch
        self.field_overrides = field_overrides if field_overrides is not None else FieldOverrides()
        self.user_kerning_mode = user_kerning_mode
        self.features = features

    def __copy__(self) -> Config:
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any]) -> Config:
        return self.deepcopy()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Config):
            return NotImplemented
        return (self.px_to_units == other.px_to_units and
                self.outline_painter == other.outline_painter and
                self.has_vertical_metrics == other.has_vertical_metrics and
                self.is_fixed_pitch == other.is_fixed_pitch and
                self.field_overrides == other.field_overrides and
                self.user_kerning_mode == other.user_kerning_mode and
                self.features == other.features)

    def copy(self) -> Config:
        return Config(
            self.px_to_units,
            self.outline_painter,
            self.has_vertical_metrics,
            self.is_fixed_pitch,
            self.field_overrides,
            self.user_kerning_mode,
            self.features,
        )

    def deepcopy(self) -> Config:
        return Config(
            self.px_to_units,
            self.outline_painter.deepcopy(),
            self.has_vertical_metrics,
            self.is_fixed_pitch,
            self.field_overrides.deepcopy(),
            self.user_kerning_mode,
            self.features.deepcopy() if self.features is not None else None,
        )
