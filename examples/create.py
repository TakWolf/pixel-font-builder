import datetime
import os
import shutil

from examples import build_dir
from pixel_font_builder import FontBuilder, WeightName, SerifStyle, SlantStyle, WidthMode, Glyph, opentype


def main():
    outputs_dir = os.path.join(build_dir, 'create')
    if os.path.exists(outputs_dir):
        shutil.rmtree(outputs_dir)
    os.makedirs(outputs_dir)

    builder = FontBuilder()
    builder.font_metrics.font_size = 12
    builder.font_metrics.horizontal_layout.ascent = 10
    builder.font_metrics.horizontal_layout.descent = -2
    builder.font_metrics.vertical_layout.ascent = 6
    builder.font_metrics.vertical_layout.descent = -6
    builder.font_metrics.x_height = 5
    builder.font_metrics.cap_height = 7

    builder.meta_info.version = '1.0.0'
    builder.meta_info.created_time = datetime.datetime.fromisoformat('2024-01-01T00:00:00Z')
    builder.meta_info.modified_time = builder.meta_info.created_time
    builder.meta_info.family_name = 'My Pixel'
    builder.meta_info.weight_name = WeightName.REGULAR
    builder.meta_info.serif_style = SerifStyle.SANS_SERIF
    builder.meta_info.slant_style = SlantStyle.NORMAL
    builder.meta_info.width_mode = WidthMode.MONOSPACED
    builder.meta_info.manufacturer = 'Pixel Font Studio'
    builder.meta_info.designer = 'TakWolf'
    builder.meta_info.description = 'A demo pixel font.'
    builder.meta_info.copyright_info = 'Copyright (c) TakWolf'
    builder.meta_info.license_info = 'This Font Software is licensed under the SIL Open Font License, Version 1.1.'
    builder.meta_info.vendor_url = 'https://github.com/TakWolf/pixel-font-builder'
    builder.meta_info.designer_url = 'https://takwolf.com'
    builder.meta_info.license_url = 'https://openfontlicense.org'
    builder.meta_info.sample_text = 'Hello World!'

    builder.character_mapping.update({
        ord('A'): 'CAP_LETTER_A',
    })

    builder.glyphs.append(Glyph(
        name='.notdef',
        advance_width=8,
        advance_height=12,
        horizontal_origin=(0, -2),
        vertical_origin_y=0,
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
            [1, 1, 1, 1, 1, 1, 1, 1],
        ],
    ))
    builder.glyphs.append(Glyph(
        name='CAP_LETTER_A',
        advance_width=8,
        advance_height=12,
        horizontal_origin=(0, -2),
        vertical_origin_y=0,
        bitmap=[
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

    builder.save_otf(os.path.join(outputs_dir, 'my-pixel.otf'))
    builder.save_otf(os.path.join(outputs_dir, 'my-pixel.woff2'), flavor=opentype.Flavor.WOFF2)
    builder.save_ttf(os.path.join(outputs_dir, 'my-font.ttf'))
    builder.save_bdf(os.path.join(outputs_dir, 'my-font.bdf'))
    builder.save_pcf(os.path.join(outputs_dir, 'my-font.pcf'))


if __name__ == '__main__':
    main()
