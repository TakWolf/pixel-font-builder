from common import path_define
from common.services import design_service
from common.services.font_service import FontConfig
from common.utils import fs_util


def main():
    fs_util.delete_dir(path_define.build_dir)

    font_config = FontConfig(path_define.glyphs_dir)
    design_service.format_glyphs(font_config)
    context = design_service.load_context(font_config)


if __name__ == '__main__':
    main()
