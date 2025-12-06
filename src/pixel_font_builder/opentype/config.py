from typing import Final

from pixel_font_builder.opentype.feature import FeatureFile
from pixel_font_builder.opentype.metric import BoundingBox
from pixel_font_builder.opentype.outline import OutlinesPainter, SolidOutlinesPainter


class FieldsOverride:
    head_bounding_box: BoundingBox | None

    def __init__(
            self,
            head_bounding_box: BoundingBox | None = None,
    ):
        self.head_bounding_box = head_bounding_box


class Config:
    DEFAULT_OUTLINES_PAINTER: Final = SolidOutlinesPainter()

    px_to_units: int
    outlines_painter: OutlinesPainter
    has_vertical_metrics: bool
    fields_override: FieldsOverride
    feature_files: list[FeatureFile]

    def __init__(
            self,
            px_to_units: int = 100,
            outlines_painter: OutlinesPainter | None = None,
            has_vertical_metrics: bool = True,
            fields_override: FieldsOverride | None = None,
            feature_files: list[FeatureFile] | None = None,
    ):
        self.px_to_units = px_to_units
        self.outlines_painter = Config.DEFAULT_OUTLINES_PAINTER if outlines_painter is None else outlines_painter
        self.has_vertical_metrics = has_vertical_metrics
        self.fields_override = FieldsOverride() if fields_override is None else fields_override
        self.feature_files = [] if feature_files is None else feature_files
