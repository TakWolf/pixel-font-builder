import os

import bdffont
import fontTools.fontBuilder

from pixel_font_builder.glyph import Glyph
from pixel_font_builder.info import MetaInfos, OpenTypeConfigs, BdfConfigs


class FontBuilder:
    def __init__(
            self,
            size: int,
            ascent: int,
            descent: int,
            x_height: int = None,
            cap_height: int = None,
            character_mapping: dict[int, str] = None,
            glyphs: list[Glyph] = None,
            meta_infos: MetaInfos = None,
            opentype_configs: OpenTypeConfigs = None,
            bdf_configs: BdfConfigs = None,
    ):
        self.size = size
        self.ascent = ascent
        self.descent = descent
        self.x_height = x_height
        self.cap_height = cap_height
        self.character_mapping = character_mapping
        self.glyphs = glyphs
        if meta_infos is None:
            meta_infos = MetaInfos()
        self.meta_infos = meta_infos
        if opentype_configs is None:
            opentype_configs = OpenTypeConfigs()
        self.opentype_configs = opentype_configs
        if bdf_configs is None:
            bdf_configs = BdfConfigs()
        self.bdf_configs = bdf_configs

    @property
    def line_height(self) -> int:
        return self.ascent - self.descent

    def check_ready(self):
        assert self.character_mapping is not None
        assert self.glyphs is not None

    def _to_opentype_builder(self, is_ttf: bool = False) -> fontTools.fontBuilder.FontBuilder:
        self.check_ready()

        units_per_em = self.size * self.opentype_configs.px_to_units

        builder = fontTools.fontBuilder.FontBuilder(
            unitsPerEm=units_per_em,
            isTTF=is_ttf,
        )

        # TODO

        return builder

    def to_otf_builder(self) -> fontTools.fontBuilder.FontBuilder:
        return self._to_opentype_builder(is_ttf=False)

    def save_otf(
            self,
            file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
            flavor: str = None,
    ):
        builder = self.to_otf_builder()
        if flavor is not None:
            builder.font.flavor = flavor
        builder.save(file_path)

    def to_ttf_builder(self) -> fontTools.fontBuilder.FontBuilder:
        return self._to_opentype_builder(is_ttf=True)

    def save_ttf(
            self,
            file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
            flavor: str = None,
    ):
        builder = self.to_ttf_builder()
        if flavor is not None:
            builder.font.flavor = flavor
        builder.save(file_path)

    def to_bdf_builder(self) -> bdffont.BdfFont:
        self.check_ready()

        builder = bdffont.BdfFont(
            point_size=self.size,
            resolution_xy=(self.bdf_configs.resolution_x, self.bdf_configs.resolution_y),
            bounding_box_size=(self.size, self.line_height),
            bounding_box_offset=(0, self.descent),
        )

        # TODO

        return builder

    def save_bdf(
            self,
            file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
            optimize_bitmap: bool = True,
    ):
        self.to_bdf_builder().save(file_path, optimize_bitmap)
