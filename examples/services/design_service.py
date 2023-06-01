import logging
import os

from examples.services import font_service
from examples.utils import glyph_util

logger = logging.getLogger('design-service')


class DesignContext:
    def __init__(
            self,
            alphabet: list[str],
            glyph_file_paths: dict[int | str, str],
    ):
        self.alphabet = alphabet
        self.glyph_file_paths = glyph_file_paths
        self.glyph_data_pool: dict[int | str, tuple[list[list[int]], int, int]] = {}

    def get_glyph_data(self, code_point: int | str) -> tuple[list[list[int]], int, int]:
        glyph_file_path = self.glyph_file_paths[code_point]
        if glyph_file_path in self.glyph_data_pool:
            glyph_data, glyph_width, glyph_height = self.glyph_data_pool[glyph_file_path]
        else:
            glyph_data, glyph_width, glyph_height = glyph_util.load_data_from_png(glyph_file_path)
            self.glyph_data_pool[glyph_file_path] = glyph_data, glyph_width, glyph_height
        return glyph_data, glyph_width, glyph_height


def format_glyphs(font_config: 'font_service.FontConfig'):
    for glyph_file_dir, _, glyph_file_names in os.walk(font_config.glyphs_dir):
        for glyph_file_name in glyph_file_names:
            if not glyph_file_name.endswith('.png'):
                continue
            glyph_file_path = os.path.join(glyph_file_dir, glyph_file_name)
            glyph_data = glyph_util.load_data_from_png(glyph_file_path)[0]
            glyph_util.save_data_to_png(glyph_data, glyph_file_path)
            logger.info(f"Format glyph file: '{glyph_file_path}'")


def load_context(font_config: 'font_service.FontConfig') -> DesignContext:
    alphabet = set()
    glyph_file_paths = {}
    for glyph_file_dir, _, glyph_file_names in os.walk(font_config.glyphs_dir):
        for glyph_file_name in glyph_file_names:
            if not glyph_file_name.endswith('.png'):
                continue
            glyph_file_path = os.path.join(glyph_file_dir, glyph_file_name)
            if glyph_file_name == 'notdef.png':
                glyph_file_paths['.notdef'] = glyph_file_path
            else:
                uni_hex_name = glyph_file_name.removesuffix('.png').upper()
                code_point = int(uni_hex_name, 16)
                c = chr(code_point)
                alphabet.add(c)
                glyph_file_paths[code_point] = glyph_file_path
    alphabet = list(alphabet)
    alphabet.sort()
    return DesignContext(alphabet, glyph_file_paths)
