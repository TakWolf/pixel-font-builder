from pixel_font_builder.opentype.feature import FeatureFile


class Config:
    px_to_units: int
    feature_files: list[FeatureFile]

    def __init__(
            self,
            px_to_units: int = 100,
            feature_files: list[FeatureFile] | None = None,
    ):
        self.px_to_units = px_to_units
        self.feature_files = [] if feature_files is None else feature_files
