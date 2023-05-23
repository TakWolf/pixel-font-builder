from common import path_define
from common.services.font_service import FontConfig


def main():
    font_config = FontConfig(path_define.glyphs_dir)


if __name__ == '__main__':
    main()
