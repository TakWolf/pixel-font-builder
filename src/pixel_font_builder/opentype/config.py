from typing import Final

from pixel_font_builder.opentype.feature import FeatureFile
from pixel_font_builder.opentype.pen import OutlinesPainter, SolidOutlinesPainter


class Config:
    DEFAULT_OUTLINES_PAINTER: Final = SolidOutlinesPainter()

    px_to_units: int
    outlines_painter: OutlinesPainter
    glyph_data_format: int
    feature_files: list[FeatureFile]

    def __init__(
            self,
            px_to_units: int = 100,
            outlines_painter: OutlinesPainter | None = None,
            glyph_data_format: int = 0,
            feature_files: list[FeatureFile] | None = None,
    ):
        self.px_to_units = px_to_units
        self.outlines_painter = Config.DEFAULT_OUTLINES_PAINTER if outlines_painter is None else outlines_painter
        self.glyph_data_format = glyph_data_format
        self.feature_files = [] if feature_files is None else feature_files
