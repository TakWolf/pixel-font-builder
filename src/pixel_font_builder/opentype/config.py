from typing import Final

from pixel_font_builder.opentype.feature import FeatureFile
from pixel_font_builder.opentype.outline import OutlinesPainter, SolidOutlinesPainter


class Config:
    DEFAULT_OUTLINES_PAINTER: Final = SolidOutlinesPainter()

    px_to_units: int
    outlines_painter: OutlinesPainter
    feature_files: list[FeatureFile]

    def __init__(
            self,
            px_to_units: int = 100,
            outlines_painter: OutlinesPainter | None = None,
            feature_files: list[FeatureFile] | None = None,
    ):
        self.px_to_units = px_to_units
        self.outlines_painter = Config.DEFAULT_OUTLINES_PAINTER if outlines_painter is None else outlines_painter
        self.feature_files = [] if feature_files is None else feature_files
