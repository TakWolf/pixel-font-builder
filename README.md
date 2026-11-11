# Pixel Font Builder

[![Python](https://img.shields.io/badge/python-3.11-brightgreen?style=flat-square)](https://www.python.org)
[![PyPI](https://img.shields.io/pypi/v/pixel-font-builder?style=flat-square)](https://pypi.org/project/pixel-font-builder/)

A library that helps create pixel style fonts.

## Installation

```shell
pip install pixel-font-builder
```

## Usage

```python
import shutil
from datetime import datetime

from examples import BUILD_DIR
from pixel_font_builder import FontBuilder, WeightName, SerifStyle, SlantStyle, WidthStyle, Glyph, MonoRaster, ColorRaster, opentype


def main() -> None:
    outputs_dir = BUILD_DIR.joinpath('create')
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
    builder.meta_info.manufacturer = 'TakWolf'
    builder.meta_info.designer = 'TakWolf'
    builder.meta_info.description = 'A pixel font'
    builder.meta_info.copyright_info = 'Copyright (c) TakWolf'
    builder.meta_info.license_info = 'This Font Software is licensed under the SIL Open Font License, Version 1.1'
    builder.meta_info.vendor_url = 'https://github.com/TakWolf/pixel-font-builder'
    builder.meta_info.designer_url = 'https://takwolf.com'
    builder.meta_info.license_url = 'https://openfontlicense.org'

    builder.glyphs.append(Glyph(
        name='.notdef',
        advance_width=8,
        advance_height=16,
        mono_raster=MonoRaster(
            horizontal_offset=(0, -2),
            vertical_offset=(-4, 0),
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
        ),
    ))

    builder.glyphs.append(Glyph(
        name='LATIN_CAPITAL_LETTER_A',
        advance_width=8,
        advance_height=16,
        mono_raster=MonoRaster(
            horizontal_offset=(0, -2),
            vertical_offset=(-4, 0),
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
        ),
    ))

    heart_bitmap = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 1, 1, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 1, 1, 1, 1, 0, 0],
        [0, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]
    builder.glyphs.append(Glyph(
        name='HEAVY_BLACK_HEART',
        advance_width=8,
        advance_height=16,
        mono_raster=MonoRaster(
            horizontal_offset=(0, -2),
            vertical_offset=(-4, 0),
            bitmap=heart_bitmap,
        ),
        color_raster=ColorRaster(
            horizontal_offset=(0, -2),
            vertical_offset=(-4, 0),
            bitmap=[
                [
                    (255, 0, 0, 255) if pixel != 0 else (0, 0, 0, 0)
                    for pixel in bitmap_row
                ]
                for bitmap_row in heart_bitmap
            ],
        ),
    ))

    builder.character_mapping[0x0041] = 'LATIN_CAPITAL_LETTER_A'
    builder.character_mapping[0x2764] = 'HEAVY_BLACK_HEART'

    builder.save_otf(outputs_dir.joinpath('my-font.otf'))
    builder.save_otf_woff(outputs_dir.joinpath('my-font.otf.woff'))
    builder.save_otf_woff2(outputs_dir.joinpath('my-font.otf.woff2'))
    builder.save_ttf(outputs_dir.joinpath('my-font.ttf'))
    builder.save_ttf_woff(outputs_dir.joinpath('my-font.ttf.woff'))
    builder.save_ttf_woff2(outputs_dir.joinpath('my-font.ttf.woff2'))
    builder.save_ms_bitmap_ttf(outputs_dir.joinpath('my-font.ms-bitmap.ttf'))
    builder.save_otb(outputs_dir.joinpath('my-font.otb'))
    builder.save_dfont(outputs_dir.joinpath('my-font.dfont'))
    builder.save_bdf(outputs_dir.joinpath('my-font.bdf'))
    builder.save_pcf(outputs_dir.joinpath('my-font.pcf'))

    builder.meta_info.family_name = 'My Font SquareDot'
    builder.opentype_config.outline_painter = opentype.SquareDotOutlinePainter()
    
    builder.save_otf(outputs_dir.joinpath('my-font-square-dot.otf'))
    builder.save_otf_woff(outputs_dir.joinpath('my-font-square-dot.otf.woff'))
    builder.save_otf_woff2(outputs_dir.joinpath('my-font-square-dot.otf.woff2'))
    builder.save_ttf(outputs_dir.joinpath('my-font-square-dot.ttf'))
    builder.save_ttf_woff(outputs_dir.joinpath('my-font-square-dot.ttf.woff'))
    builder.save_ttf_woff2(outputs_dir.joinpath('my-font-square-dot.ttf.woff2'))

    builder.meta_info.family_name = 'My Font CircleDot'
    builder.opentype_config.outline_painter = opentype.CircleDotOutlinePainter()
    
    builder.save_otf(outputs_dir.joinpath('my-font-circle-dot.otf'))
    builder.save_otf_woff(outputs_dir.joinpath('my-font-circle-dot.otf.woff'))
    builder.save_otf_woff2(outputs_dir.joinpath('my-font-circle-dot.otf.woff2'))
    builder.save_ttf(outputs_dir.joinpath('my-font-circle-dot.ttf'))
    builder.save_ttf_woff(outputs_dir.joinpath('my-font-circle-dot.ttf.woff'))
    builder.save_ttf_woff2(outputs_dir.joinpath('my-font-circle-dot.ttf.woff2'))

    builder.opentype_config.outline_painter = opentype.Config.DEFAULT_OUTLINE_PAINTER

    builder.meta_info.family_name = 'My Font Color COLR'
    builder.opentype_config.color_table_formats = {
        opentype.ColorTableFormat.COLR,
    }

    builder.save_otf(outputs_dir.joinpath('my-font.colr.otf'))
    builder.save_otf_woff(outputs_dir.joinpath('my-font.colr.otf.woff'))
    builder.save_otf_woff2(outputs_dir.joinpath('my-font.colr.otf.woff2'))
    builder.save_ttf(outputs_dir.joinpath('my-font.colr.ttf'))
    builder.save_ttf_woff(outputs_dir.joinpath('my-font.colr.ttf.woff'))
    builder.save_ttf_woff2(outputs_dir.joinpath('my-font.colr.ttf.woff2'))

    builder.meta_info.family_name = 'My Font Color CBDT'
    builder.opentype_config.color_table_formats = {
        opentype.ColorTableFormat.CBDT,
    }

    builder.save_otf(outputs_dir.joinpath('my-font.cbdt.otf'))
    builder.save_otf_woff(outputs_dir.joinpath('my-font.cbdt.otf.woff'))
    builder.save_otf_woff2(outputs_dir.joinpath('my-font.cbdt.otf.woff2'))
    builder.save_ttf(outputs_dir.joinpath('my-font.cbdt.ttf'))
    builder.save_ttf_woff(outputs_dir.joinpath('my-font.cbdt.ttf.woff'))
    builder.save_ttf_woff2(outputs_dir.joinpath('my-font.cbdt.ttf.woff2'))

    builder.meta_info.family_name = 'My Font Color SBIX'
    builder.opentype_config.color_table_formats = {
        opentype.ColorTableFormat.SBIX,
    }

    builder.save_otf(outputs_dir.joinpath('my-font.sbix.otf'))
    builder.save_otf_woff(outputs_dir.joinpath('my-font.sbix.otf.woff'))
    builder.save_otf_woff2(outputs_dir.joinpath('my-font.sbix.otf.woff2'))
    builder.save_ttf(outputs_dir.joinpath('my-font.sbix.ttf'))
    builder.save_ttf_woff(outputs_dir.joinpath('my-font.sbix.ttf.woff'))
    builder.save_ttf_woff2(outputs_dir.joinpath('my-font.sbix.ttf.woff2'))

    builder.meta_info.family_name = 'My Font Color All'
    builder.opentype_config.color_table_formats = {
        opentype.ColorTableFormat.COLR,
        opentype.ColorTableFormat.CBDT,
        opentype.ColorTableFormat.SBIX,
    }

    builder.save_otf(outputs_dir.joinpath('my-font.color-all.otf'))
    builder.save_otf_woff(outputs_dir.joinpath('my-font.color-all.otf.woff'))
    builder.save_otf_woff2(outputs_dir.joinpath('my-font.color-all.otf.woff2'))
    builder.save_ttf(outputs_dir.joinpath('my-font.color-all.ttf'))
    builder.save_ttf_woff(outputs_dir.joinpath('my-font.color-all.ttf.woff'))
    builder.save_ttf_woff2(outputs_dir.joinpath('my-font.color-all.ttf.woff2'))


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
| [OpenType](https://learn.microsoft.com/en-us/typography/opentype/) | `.otf`, `.otc` |
| [TrueType](https://learn.microsoft.com/en-us/typography/truetype/) | `.ttf`, `.ttc` |
| [WOFF File Format 1.0](https://www.w3.org/TR/WOFF/) | `.otf.woff`, `.ttf.woff` |
| [WOFF File Format 2.0](https://www.w3.org/TR/WOFF2/) | `.otf.woff2`, `.ttf.woff2` |
| [Microsoft Bitmap Only SFNT](https://fontforge.org/docs/techref/bitmaponlysfnt.html#ms) | `.ms-bitmap.ttf` |
| [X11 OpenType Bitmap](https://fontforge.org/docs/techref/bitmaponlysfnt.html#x11-unix-linux) | `.otb` |
| [Macintosh Datafork TrueType](https://fontforge.org/docs/techref/macformats.html) | `.dfont` |
| [Glyph Bitmap Distribution Format](https://en.wikipedia.org/wiki/Glyph_Bitmap_Distribution_Format) | `.bdf` |
| [Portable Compiled Format](https://en.wikipedia.org/wiki/Portable_Compiled_Format) | `.pcf` |

## Supported Color Table Formats

- [COLR](https://learn.microsoft.com/en-us/typography/opentype/spec/colr)
- [CBDT](https://learn.microsoft.com/en-us/typography/opentype/spec/cbdt)
- [sbix](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6sbix.html)

## Dependencies

- [FontTools](https://github.com/fonttools/fonttools)
- [BdfFont - Python](https://github.com/TakWolf/bdffont-python)
- [PcfFont - Python](https://github.com/TakWolf/pcffont-python)

## References

- [Microsoft - OpenType Specification](https://learn.microsoft.com/en-us/typography/opentype/spec/)
- [FreeType Glyph Conventions - Glyph Metrics](https://freetype.org/freetype2/docs/glyphs/glyphs-3.html)
- [OpenType Feature File Specification](https://adobe-type-tools.github.io/afdko/OpenTypeFeatureFileSpecification.html)
- [FontForge - Several formats for bitmap only sfnts](https://fontforge.org/docs/techref/bitmaponlysfnt.html)

## License

[MIT License](LICENSE)
