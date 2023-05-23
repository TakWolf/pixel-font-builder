import logging
import os
import tomllib

logger = logging.getLogger('font-service')


class FontConfig:
    def __init__(
            self,
            glyphs_dir: str | bytes | os.PathLike[str] | os.PathLike[bytes],
    ):
        self.glyphs_dir = glyphs_dir

        config_file_path = os.path.join(glyphs_dir, 'config.toml')
        with open(config_file_path, 'rb') as file:
            config_data = tomllib.load(file)['font']

        self.size = config_data['size']
        self.line_height = config_data['line_height']
        self.box_origin_y = config_data['box_origin_y']
        self.ascent = round((self.line_height - self.size) / 2 + self.box_origin_y)
        self.descent = self.ascent - self.line_height
        self.x_height = config_data['x_height']
        self.cap_height = config_data['cap_height']
