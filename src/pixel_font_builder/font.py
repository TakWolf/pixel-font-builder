import math
import os

import bdffont
import bdffont.xlfd
import fontTools.fontBuilder

from pixel_font_builder.glyph import Glyph
from pixel_font_builder.info import MetaInfos, OpenTypeConfigs, BdfConfigs, OpenTypeFlavor


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

    def _check_ready(self):
        assert self.character_mapping is not None
        assert self.glyphs is not None

    def _to_opentype_builder(self, is_ttf: bool = False, flavor: OpenTypeFlavor = None) -> fontTools.fontBuilder.FontBuilder:
        self._check_ready()

        units_per_em = self.size * self.opentype_configs.px_to_units

        builder = fontTools.fontBuilder.FontBuilder(
            unitsPerEm=units_per_em,
            isTTF=is_ttf,
        )

        # TODO

        if flavor is not None:
            builder.font.flavor = flavor

        return builder

    def to_otf_builder(self, flavor: OpenTypeFlavor = None) -> fontTools.fontBuilder.FontBuilder:
        return self._to_opentype_builder(False, flavor)

    def save_otf(
            self,
            file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
            flavor: OpenTypeFlavor = None,
    ):
        self.to_otf_builder(flavor).save(file_path)

    def to_ttf_builder(self, flavor: OpenTypeFlavor = None) -> fontTools.fontBuilder.FontBuilder:
        return self._to_opentype_builder(True, flavor)

    def save_ttf(
            self,
            file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
            flavor: OpenTypeFlavor = None,
    ):
        self.to_ttf_builder(flavor).save(file_path)

    def _create_bdf_glyph(self, code_point: int, glyph: Glyph) -> bdffont.BdfGlyph:
        scalable_width_x = math.ceil((glyph.advance_width / self.size) * (72 / self.bdf_configs.resolution_x) * 1000)
        if glyph.data is None:
            glyph_width = 0
            glyph_height = 0
        else:
            glyph_width = len(glyph.data[0])
            glyph_height = len(glyph.data)
        return bdffont.BdfGlyph(
            name=glyph.name,
            code_point=code_point,
            scalable_width=(scalable_width_x, 0),
            device_width=(glyph.advance_width, 0),
            bounding_box_size=(glyph_width, glyph_height),
            bounding_box_offset=glyph.offset,
            bitmap=glyph.data,
        )

    def to_bdf_builder(self) -> bdffont.BdfFont:
        self._check_ready()

        if -1 in self.character_mapping:
            raise Exception("Code '-1' is reserved for glyph '.notdef'")

        name_to_glyph = {glyph.name: glyph for glyph in self.glyphs}
        if '.notdef' not in name_to_glyph:
            raise Exception("Need to provide a glyph named '.notdef'")

        builder = bdffont.BdfFont(
            point_size=self.size,
            resolution_xy=(self.bdf_configs.resolution_x, self.bdf_configs.resolution_y),
            bounding_box_size=(self.size, self.line_height),
            bounding_box_offset=(0, self.descent),
        )

        builder.add_glyph(self._create_bdf_glyph(-1, name_to_glyph['.notdef']))
        for code_point, glyph_name in self.character_mapping.items():
            builder.add_glyph(self._create_bdf_glyph(code_point, name_to_glyph[glyph_name]))

        builder.properties.foundry = self.meta_infos.foundry
        builder.properties.family_name = self.meta_infos.family_name
        # builder.properties.weight_name =
        # builder.properties.slant =
        # builder.properties.setwidth_name =
        # builder.properties.add_style_name =
        builder.properties.pixel_size = self.size
        builder.properties.point_size = self.size * 100
        builder.properties.resolution_x = self.bdf_configs.resolution_x
        builder.properties.resolution_y = self.bdf_configs.resolution_y
        # builder.properties.spacing =
        builder.properties.average_width = round(sum([glyph.scalable_width_x for glyph in builder.code_point_to_glyph.values()]) / builder.get_glyphs_count())
        builder.properties.charset_registry = bdffont.xlfd.CharsetRegistry.ISO10646
        builder.properties.charset_encoding = '1'

        builder.properties.default_char = -1
        builder.properties.font_ascent = self.ascent
        builder.properties.font_descent = self.descent
        builder.properties.x_height = self.x_height
        builder.properties.cap_height = self.cap_height

        builder.properties.font_version = self.meta_infos.version
        builder.properties.copyright = self.meta_infos.copyright_info
        builder.properties['LICENSE'] = self.meta_infos.license_description

        builder.generate_xlfd_font_name()

        return builder

    def save_bdf(
            self,
            file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
            optimize_bitmap: bool = True,
    ):
        self.to_bdf_builder().save(file_path, optimize_bitmap)
