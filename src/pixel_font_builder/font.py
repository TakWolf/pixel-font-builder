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
    ):
        self.size = size
        self.ascent = ascent
        self.descent = descent
        self.x_height = x_height
        self.cap_height = cap_height

        self.character_mapping: dict[int, str] = {}
        self._name_to_glyph: dict[str, Glyph] = {}

        self.meta_infos = MetaInfos()
        self.opentype_configs = OpenTypeConfigs()
        self.bdf_configs = BdfConfigs()

    @property
    def line_height(self) -> int:
        return self.ascent - self.descent

    def get_glyph(self, name: str) -> Glyph | None:
        return self._name_to_glyph.get(name, None)

    def get_glyphs(self) -> list[Glyph]:
        return list(self._name_to_glyph.values())

    def get_glyphs_count(self) -> int:
        return len(self._name_to_glyph)

    def set_glyph(self, glyph: Glyph):
        self._name_to_glyph[glyph.name] = glyph

    def add_glyph(self, glyph: Glyph):
        if glyph.name in self._name_to_glyph:
            raise Exception(f"Glyph '{glyph.name}' already exists")
        self._name_to_glyph[glyph.name] = glyph

    def add_glyphs(self, glyphs: list[Glyph]):
        for glyph in glyphs:
            self.add_glyph(glyph)

    def remove_glyph(self, name: str) -> Glyph | None:
        return self._name_to_glyph.pop(name, None)

    def check_ready(self):
        if any(code_point < 0 for code_point in self.character_mapping):
            raise Exception(f"Code points must >= 0")
        if '.notdef' not in self._name_to_glyph:
            raise Exception("Need to provide a glyph named '.notdef'")

    # ========
    # OpenType
    # ========

    def _to_opentype_builder(self, is_ttf: bool = False, flavor: OpenTypeFlavor = None) -> fontTools.fontBuilder.FontBuilder:
        self.check_ready()

        units_per_em = self.size * self.opentype_configs.px_to_units

        builder = fontTools.fontBuilder.FontBuilder(units_per_em, isTTF=is_ttf)

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

    # ==========================
    # Bitmap Distribution Format
    # ==========================

    def _create_bdf_glyph(self, code_point: int, glyph_name: str) -> bdffont.BdfGlyph:
        glyph = self._name_to_glyph[glyph_name]
        scalable_width_x = math.ceil((glyph.advance_width / self.size) * (72 / self.bdf_configs.resolution_x) * 1000)
        return bdffont.BdfGlyph(
            name=glyph.name,
            code_point=code_point,
            scalable_width=(scalable_width_x, 0),
            device_width=(glyph.advance_width, 0),
            bounding_box_size=glyph.size,
            bounding_box_offset=glyph.offset,
            bitmap=glyph.data,
        )

    def to_bdf_builder(self) -> bdffont.BdfFont:
        self.check_ready()

        builder = bdffont.BdfFont(
            point_size=self.size,
            resolution_xy=(self.bdf_configs.resolution_x, self.bdf_configs.resolution_y),
            bounding_box_size=(self.size, self.line_height),
            bounding_box_offset=(0, self.descent),
        )

        builder.add_glyph(self._create_bdf_glyph(-1, '.notdef'))
        for code_point, glyph_name in self.character_mapping.items():
            builder.add_glyph(self._create_bdf_glyph(code_point, glyph_name))

        builder.properties.foundry = self.meta_infos.foundry
        builder.properties.family_name = self.meta_infos.family_name
        # builder.properties.weight_name =
        # builder.properties.slant =
        # builder.properties.setwidth_name =
        # builder.properties.add_style_name =
        builder.properties.pixel_size = self.size
        builder.properties.point_size = self.size * 10
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
