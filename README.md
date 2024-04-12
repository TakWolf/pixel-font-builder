# Pixel Font Builder

[![Python](https://img.shields.io/badge/python-3.11-brightgreen)](https://www.python.org)
[![PyPI](https://img.shields.io/pypi/v/pixel-font-builder)](https://pypi.org/project/pixel-font-builder/)

A library that helps create pixel style fonts.

## Installation

```shell
pip install pixel-font-builder
```

## Usage

```python
import os
import shutil

from examples import build_dir
from pixel_font_builder import FontBuilder, StyleName, SerifMode, WidthMode, Glyph, opentype


def main():
    outputs_dir = os.path.join(build_dir, 'create')
    if os.path.exists(outputs_dir):
        shutil.rmtree(outputs_dir)
    os.makedirs(outputs_dir)

    builder = FontBuilder(12)

    builder.meta_info.version = '1.0.0'
    builder.meta_info.family_name = 'My Pixel'
    builder.meta_info.style_name = StyleName.REGULAR
    builder.meta_info.serif_mode = SerifMode.SANS_SERIF
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

    builder.horizontal_header.ascent = 10
    builder.horizontal_header.descent = -2

    builder.vertical_header.ascent = 10
    builder.vertical_header.descent = -2

    builder.os2_config.x_height = 5
    builder.os2_config.cap_height = 7

    builder.character_mapping.update({
        ord('A'): 'CAP_LETTER_A',
    })

    builder.glyphs.append(Glyph(
        name='.notdef',
        advance_width=8,
        advance_height=12,
        horizontal_origin=(0, -2),
        vertical_origin_y=0,
        data=[
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
        data=[
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


if __name__ == '__main__':
    main()
```

## Dependencies

- [FontTools](https://github.com/fonttools/fonttools)
- [Brotli](https://github.com/google/brotli)
- [BdfFont](https://github.com/TakWolf/bdffont)
- [PcfFont](https://github.com/TakWolf/pcffont)

## License

Under the [MIT license](LICENSE).
