# Pixel Font Builder

[![Python](https://img.shields.io/badge/python-3.12-brightgreen)](https://www.python.org)
[![PyPI](https://img.shields.io/pypi/v/pixel-font-builder)](https://pypi.org/project/pixel-font-builder/)

A library that helps create pixel style fonts.

## Installation

```shell
pip install pixel-font-builder
```

## Usage

```python
import datetime
import shutil
from typing import Literal

from examples import build_dir
from pixel_font_builder import FontBuilder, WeightName, SerifStyle, SlantStyle, WidthStyle, Glyph, opentype


def _create_builder(outlines_style: Literal['SquareDot', 'CircleDot'] | None = None) -> FontBuilder:
    builder = FontBuilder()
    builder.font_metric.font_size = 12
    builder.font_metric.horizontal_layout.ascent = 10
    builder.font_metric.horizontal_layout.descent = -2
    builder.font_metric.vertical_layout.ascent = 6
    builder.font_metric.vertical_layout.descent = -6
    builder.font_metric.x_height = 5
    builder.font_metric.cap_height = 7

    builder.meta_info.version = '1.0.0'
    builder.meta_info.created_time = datetime.datetime.fromisoformat('2024-01-01T00:00:00Z')
    builder.meta_info.modified_time = builder.meta_info.created_time
    builder.meta_info.family_name = 'My Pixel'
    if outlines_style is not None:
        builder.meta_info.family_name = f'{builder.meta_info.family_name} {outlines_style}'
    builder.meta_info.weight_name = WeightName.REGULAR
    builder.meta_info.serif_style = SerifStyle.SANS_SERIF
    builder.meta_info.slant_style = SlantStyle.NORMAL
    builder.meta_info.width_style = WidthStyle.MONOSPACED
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
        horizontal_origin=(0, -2),
        advance_width=8,
        vertical_origin=(-4, 0),
        advance_height=12,
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
        horizontal_origin=(0, -2),
        advance_width=8,
        vertical_origin=(-4, 0),
        advance_height=12,
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

    if outlines_style == 'SquareDot':
        builder.opentype_config.outlines_painter = opentype.SquareDotOutlinesPainter()
    elif outlines_style == 'CircleDot':
        builder.opentype_config.outlines_painter = opentype.CircleDotOutlinesPainter()

    return builder


def main():
    outputs_dir = build_dir.joinpath('create')
    if outputs_dir.exists():
        shutil.rmtree(outputs_dir)
    outputs_dir.mkdir(parents=True)

    builder = _create_builder()
    builder.save_otf(outputs_dir.joinpath('my-pixel.otf'))
    builder.save_otf(outputs_dir.joinpath('my-pixel.woff2'), flavor=opentype.Flavor.WOFF2)
    builder.save_ttf(outputs_dir.joinpath('my-font.ttf'))
    builder.save_bdf(outputs_dir.joinpath('my-font.bdf'))
    builder.save_pcf(outputs_dir.joinpath('my-font.pcf'))

    square_dot_builder = _create_builder('SquareDot')
    square_dot_builder.save_otf(outputs_dir.joinpath('my-pixel-square_dot.otf'))
    square_dot_builder.save_otf(outputs_dir.joinpath('my-pixel-square_dot.woff2'), flavor=opentype.Flavor.WOFF2)
    square_dot_builder.save_ttf(outputs_dir.joinpath('my-font-square_dot.ttf'))

    circle_dot_builder = _create_builder('CircleDot')
    circle_dot_builder.save_otf(outputs_dir.joinpath('my-pixel-circle_dot.otf'))
    circle_dot_builder.save_otf(outputs_dir.joinpath('my-pixel-circle_dot.woff2'), flavor=opentype.Flavor.WOFF2)
    circle_dot_builder.save_ttf(outputs_dir.joinpath('my-font-circle_dot.ttf'))


if __name__ == '__main__':
    main()
```

## Coordinate Systems

Use the same coordinate systems as OpenType.

### Horizontal Layout

![Horizontal Layout](https://freetype.org/freetype2/docs/glyphs/glyph-metrics-3.svg)

### Vertical Layout

![Vertical Layout](https://freetype.org/freetype2/docs/glyphs/glyph-metrics-4.svg)

## Supported Output Formats

| Format | File Extension |
|---|---|
| [OpenType](https://learn.microsoft.com/en-us/typography/opentype/) | `.otf`, `.otc`, `.woff`, `.woff2` |
| [TrueType](https://learn.microsoft.com/en-us/typography/truetype/) | `.ttf`, `.ttc`, `.woff`, `.woff2` |
| [Glyph Bitmap Distribution Format](https://en.wikipedia.org/wiki/Glyph_Bitmap_Distribution_Format) | `.bdf` |
| [Portable Compiled Format](https://en.wikipedia.org/wiki/Portable_Compiled_Format) | `.pcf` |

## Dependencies

- [FontTools](https://github.com/fonttools/fonttools)
- [BdfFont](https://github.com/TakWolf/bdffont)
- [PcfFont](https://github.com/TakWolf/pcffont)

## References

- [FreeType Glyph Conventions - Glyph Metrics](https://freetype.org/freetype2/docs/glyphs/glyphs-3.html)
- [OpenType Feature File Specification](https://adobe-type-tools.github.io/afdko/OpenTypeFeatureFileSpecification.html)

## License

Under the [MIT license](LICENSE).
