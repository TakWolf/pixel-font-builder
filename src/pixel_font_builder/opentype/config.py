from typing import Final

from pixel_font_builder.opentype.feature import FeatureFile
from pixel_font_builder.opentype.outline import OutlinesPainter, SolidOutlinesPainter


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
    ):
        self.head_x_min = head_x_min
        self.head_y_min = head_y_min
        self.head_x_max = head_x_max
        self.head_y_max = head_y_max
        self.os2_x_avg_char_width = os2_x_avg_char_width


class Config:
    DEFAULT_OUTLINES_PAINTER: Final = SolidOutlinesPainter()

    px_to_units: int
    outlines_painter: OutlinesPainter
    has_vertical_metrics: bool
    is_monospaced: bool
    fields_override: FieldsOverride
    feature_files: list[FeatureFile]

    def __init__(
            self,
            px_to_units: int = 100,
            outlines_painter: OutlinesPainter | None = None,
            has_vertical_metrics: bool = True,
            is_monospaced: bool = False,
            fields_override: FieldsOverride | None = None,
            feature_files: list[FeatureFile] | None = None,
    ):
        self.px_to_units = px_to_units
        self.outlines_painter = Config.DEFAULT_OUTLINES_PAINTER if outlines_painter is None else outlines_painter
        self.has_vertical_metrics = has_vertical_metrics
        self.is_monospaced = is_monospaced
        self.fields_override = FieldsOverride() if fields_override is None else fields_override
        self.feature_files = [] if feature_files is None else feature_files
