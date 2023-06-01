import logging
import os.path

from examples import build_dir, outputs_dir, glyphs_dir
from examples.services import font_service, design_service
from examples.services.font_service import FontConfig
from examples.utils import fs_util
from pixel_font_builder import OpenTypeFlavor

logging.basicConfig(level=logging.DEBUG)


def main():
    fs_util.delete_dir(build_dir)
    fs_util.make_dirs_if_not_exists(outputs_dir)

    font_config = FontConfig(glyphs_dir)
    design_service.format_glyphs(font_config)
    design_context = design_service.load_context(font_config)
    font_builder = font_service.create_font_builder(font_config, design_context)
    font_builder.save_otf(os.path.join(outputs_dir, 'demo.otf'))
    font_builder.save_otf(os.path.join(outputs_dir, 'demo.woff2'), flavor=OpenTypeFlavor.WOFF2)
    font_builder.save_ttf(os.path.join(outputs_dir, 'demo.ttf'))
    font_builder.save_bdf(os.path.join(outputs_dir, 'demo.bdf'))


if __name__ == '__main__':
    main()
