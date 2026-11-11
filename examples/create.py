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
