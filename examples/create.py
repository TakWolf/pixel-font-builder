import shutil
from datetime import datetime

from examples import build_dir
from pixel_font_builder import FontBuilder, WeightName, SerifStyle, SlantStyle, WidthStyle, Glyph, opentype


def main():
    outputs_dir = build_dir.joinpath('create')
    if outputs_dir.exists():
        shutil.rmtree(outputs_dir)
    outputs_dir.mkdir(parents=True)

    builder = FontBuilder()
    builder.font_metric.font_size = 16
    builder.font_metric.horizontal_layout.ascent = 14
    builder.font_metric.horizontal_layout.descent = -2
    builder.font_metric.vertical_layout.ascent = 8
    builder.font_metric.vertical_layout.descent = -8
    builder.font_metric.x_height = 7
    builder.font_metric.cap_height = 10
    builder.font_metric.underline_position = -2
    builder.font_metric.underline_thickness = 1
    builder.font_metric.strikeout_position = 6
    builder.font_metric.strikeout_thickness = 1

    builder.meta_info.version = '1.0.0'
    builder.meta_info.created_time = datetime.fromisoformat('2024-01-01T00:00:00Z')
    builder.meta_info.modified_time = builder.meta_info.created_time
    builder.meta_info.family_name = 'My Font'
    builder.meta_info.weight_name = WeightName.REGULAR
    builder.meta_info.serif_style = SerifStyle.SANS_SERIF
    builder.meta_info.slant_style = SlantStyle.NORMAL
    builder.meta_info.width_style = WidthStyle.MONOSPACED
    builder.meta_info.manufacturer = 'Pixel Font Studio'
    builder.meta_info.designer = 'TakWolf'
    builder.meta_info.description = 'A pixel font'
    builder.meta_info.copyright_info = 'Copyright (c) TakWolf'
    builder.meta_info.license_info = 'This Font Software is licensed under the SIL Open Font License, Version 1.1'
    builder.meta_info.vendor_url = 'https://github.com/TakWolf/pixel-font-builder'
    builder.meta_info.designer_url = 'https://takwolf.com'
    builder.meta_info.license_url = 'https://openfontlicense.org'

    builder.character_mapping.update({
        65: 'CAP_LETTER_A',
    })

    builder.glyphs.append(Glyph(
        name='.notdef',
        horizontal_offset=(0, -2),
        advance_width=8,
        vertical_offset=(-4, 0),
        advance_height=16,
        bitmap=[
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
        ],
    ))
    builder.glyphs.append(Glyph(
        name='CAP_LETTER_A',
        horizontal_offset=(0, -2),
        advance_width=8,
        vertical_offset=(-4, 0),
        advance_height=16,
        bitmap=[
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 1, 0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0, 1, 0, 0],
            [0, 1, 0, 0, 0, 0, 1, 0],
            [0, 1, 0, 0, 0, 0, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 0, 0, 0, 0, 1, 0],
            [0, 1, 0, 0, 0, 0, 1, 0],
            [0, 1, 0, 0, 0, 0, 1, 0],
            [0, 1, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ],
    ))

    builder.save_otf(outputs_dir.joinpath('my-font.otf'))
    builder.save_otf(outputs_dir.joinpath('my-font.otf.woff'), flavor=opentype.Flavor.WOFF)
    builder.save_otf(outputs_dir.joinpath('my-font.otf.woff2'), flavor=opentype.Flavor.WOFF2)
    builder.save_ttf(outputs_dir.joinpath('my-font.ttf'))
    builder.save_ttf(outputs_dir.joinpath('my-font.ttf.woff'), flavor=opentype.Flavor.WOFF)
    builder.save_ttf(outputs_dir.joinpath('my-font.ttf.woff2'), flavor=opentype.Flavor.WOFF2)
    builder.save_bdf(outputs_dir.joinpath('my-font.bdf'))
    builder.save_pcf(outputs_dir.joinpath('my-font.pcf'))

    builder.meta_info.family_name = 'My Font SquareDot'
    builder.opentype_config.outlines_painter = opentype.SquareDotOutlinesPainter()
    builder.save_otf(outputs_dir.joinpath('my-font-square_dot.otf'))
    builder.save_otf(outputs_dir.joinpath('my-font-square_dot.otf.woff'), flavor=opentype.Flavor.WOFF)
    builder.save_otf(outputs_dir.joinpath('my-font-square_dot.otf.woff2'), flavor=opentype.Flavor.WOFF2)
    builder.save_ttf(outputs_dir.joinpath('my-font-square_dot.ttf'))
    builder.save_ttf(outputs_dir.joinpath('my-font-square_dot.ttf.woff'), flavor=opentype.Flavor.WOFF)
    builder.save_ttf(outputs_dir.joinpath('my-font-square_dot.ttf.woff2'), flavor=opentype.Flavor.WOFF2)

    builder.meta_info.family_name = 'My Font CircleDot'
    builder.opentype_config.outlines_painter = opentype.CircleDotOutlinesPainter()
    builder.save_otf(outputs_dir.joinpath('my-font-circle_dot.otf'))
    builder.save_otf(outputs_dir.joinpath('my-font-circle_dot.otf.woff'), flavor=opentype.Flavor.WOFF)
    builder.save_otf(outputs_dir.joinpath('my-font-circle_dot.otf.woff2'), flavor=opentype.Flavor.WOFF2)
    builder.save_ttf(outputs_dir.joinpath('my-font-circle_dot.ttf'))
    builder.save_ttf(outputs_dir.joinpath('my-font-circle_dot.ttf.woff'), flavor=opentype.Flavor.WOFF)
    builder.save_ttf(outputs_dir.joinpath('my-font-circle_dot.ttf.woff2'), flavor=opentype.Flavor.WOFF2)


if __name__ == '__main__':
    main()
