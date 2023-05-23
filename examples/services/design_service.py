import logging
import os

from examples.services.font_service import FontConfig
from examples.utils import glyph_util

logger = logging.getLogger('design-service')


class DesignContext:
    def __init__(
            self,
            alphabet: list[str],
            not_def_glyph_file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
            code_point_to_glyph_file_path: dict[int, str | bytes | os.PathLike[str] | os.PathLike[bytes]],
    ):
        self.alphabet = alphabet
        self.not_def_glyph_file_path = not_def_glyph_file_path
        self.code_point_to_glyph_file_path = code_point_to_glyph_file_path


def format_glyphs(font_config: FontConfig):
    for glyph_file_dir, _, glyph_file_names in os.walk(font_config.glyphs_dir):
        for glyph_file_name in glyph_file_names:
            if not glyph_file_name.endswith('.png'):
                continue
            glyph_file_path = os.path.join(glyph_file_dir, glyph_file_name)
            glyph_data = glyph_util.load_data_from_png(glyph_file_path)[0]
            glyph_util.save_data_to_png(glyph_data, glyph_file_path)
            logger.info(f'format glyph file: {glyph_file_path}')


def load_context(font_config: FontConfig) -> DesignContext:
    alphabet = set()
    not_def_glyph_file_path = None
    code_point_to_glyph_file_path = {}
    for glyph_file_dir, _, glyph_file_names in os.walk(font_config.glyphs_dir):
        for glyph_file_name in glyph_file_names:
            if not glyph_file_name.endswith('.png'):
                continue
            glyph_file_path = os.path.join(glyph_file_dir, glyph_file_name)
            if glyph_file_name == 'notdef.png':
                not_def_glyph_file_path = glyph_file_path
            else:
                uni_hex_name = glyph_file_name.removesuffix('.png').upper()
                code_point = int(uni_hex_name, 16)
                c = chr(code_point)
                alphabet.add(c)
                code_point_to_glyph_file_path[code_point] = glyph_file_path
    alphabet = list(alphabet)
    alphabet.sort()
    return DesignContext(alphabet, not_def_glyph_file_path, code_point_to_glyph_file_path)
