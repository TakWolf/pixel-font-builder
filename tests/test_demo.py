import shutil
from pathlib import Path

from pixel_font_builder import FontBuilder, FontCollectionBuilder, opentype


def test_demo(demo_builder: FontBuilder, demo_collection_builder: FontCollectionBuilder, build_dir: Path) -> None:
    outputs_dir = build_dir.joinpath('demo')
    if outputs_dir.exists():
        shutil.rmtree(outputs_dir)
    outputs_dir.mkdir(parents=True)

    demo_builder = demo_builder.copy()
    demo_builder.meta_info = demo_builder.meta_info.copy()
    demo_builder.opentype_config = demo_builder.opentype_config.copy()

    demo_builder.save_otf(outputs_dir.joinpath('demo.otf'))
    demo_builder.save_otf_woff(outputs_dir.joinpath('demo.otf.woff'))
    demo_builder.save_otf_woff2(outputs_dir.joinpath('demo.otf.woff2'))
    demo_builder.save_ttf(outputs_dir.joinpath('demo.ttf'))
    demo_builder.save_ttf_woff(outputs_dir.joinpath('demo.ttf.woff'))
    demo_builder.save_ttf_woff2(outputs_dir.joinpath('demo.ttf.woff2'))
    demo_builder.save_ms_bitmap_ttf(outputs_dir.joinpath('demo.ms-bitmap.ttf'))
    demo_builder.save_otb(outputs_dir.joinpath('demo.otb'))
    demo_builder.save_dfont(outputs_dir.joinpath('demo.dfont'))
    demo_builder.save_bdf(outputs_dir.joinpath('demo.bdf'))
    demo_builder.save_pcf(outputs_dir.joinpath('demo.pcf'))

    demo_builder.meta_info.family_name = 'Demo SquareDot'
    demo_builder.opentype_config.outline_painter = opentype.SquareDotOutlinePainter()

    demo_builder.save_otf(outputs_dir.joinpath('demo-square-dot.otf'))
    demo_builder.save_otf_woff(outputs_dir.joinpath('demo-square-dot.otf.woff'))
    demo_builder.save_otf_woff2(outputs_dir.joinpath('demo-square-dot.otf.woff2'))
    demo_builder.save_ttf(outputs_dir.joinpath('demo-square-dot.ttf'))
    demo_builder.save_ttf_woff(outputs_dir.joinpath('demo-square-dot.ttf.woff'))
    demo_builder.save_ttf_woff2(outputs_dir.joinpath('demo-square-dot.ttf.woff2'))

    demo_builder.meta_info.family_name = 'Demo CircleDot'
    demo_builder.opentype_config.outline_painter = opentype.CircleDotOutlinePainter()

    demo_builder.save_otf(outputs_dir.joinpath('demo-circle-dot.otf'))
    demo_builder.save_otf_woff(outputs_dir.joinpath('demo-circle-dot.otf.woff'))
    demo_builder.save_otf_woff2(outputs_dir.joinpath('demo-circle-dot.otf.woff2'))
    demo_builder.save_ttf(outputs_dir.joinpath('demo-circle-dot.ttf'))
    demo_builder.save_ttf_woff(outputs_dir.joinpath('demo-circle-dot.ttf.woff'))
    demo_builder.save_ttf_woff2(outputs_dir.joinpath('demo-circle-dot.ttf.woff2'))

    demo_builder.opentype_config.outline_painter = opentype.Config.DEFAULT_OUTLINE_PAINTER

    demo_builder.meta_info.family_name = 'Demo Color COLR'
    demo_builder.opentype_config.color_table_formats = {
        opentype.ColorTableFormat.COLR,
    }

    demo_builder.save_otf(outputs_dir.joinpath('demo.colr.otf'))
    demo_builder.save_otf_woff(outputs_dir.joinpath('demo.colr.otf.woff'))
    demo_builder.save_otf_woff2(outputs_dir.joinpath('demo.colr.otf.woff2'))
    demo_builder.save_ttf(outputs_dir.joinpath('demo.colr.ttf'))
    demo_builder.save_ttf_woff(outputs_dir.joinpath('demo.colr.ttf.woff'))
    demo_builder.save_ttf_woff2(outputs_dir.joinpath('demo.colr.ttf.woff2'))

    demo_builder.meta_info.family_name = 'Demo Color CBDT'
    demo_builder.opentype_config.color_table_formats = {
        opentype.ColorTableFormat.CBDT,
    }

    demo_builder.save_otf(outputs_dir.joinpath('demo.cbdt.otf'))
    demo_builder.save_otf_woff(outputs_dir.joinpath('demo.cbdt.otf.woff'))
    demo_builder.save_otf_woff2(outputs_dir.joinpath('demo.cbdt.otf.woff2'))
    demo_builder.save_ttf(outputs_dir.joinpath('demo.cbdt.ttf'))
    demo_builder.save_ttf_woff(outputs_dir.joinpath('demo.cbdt.ttf.woff'))
    demo_builder.save_ttf_woff2(outputs_dir.joinpath('demo.cbdt.ttf.woff2'))

    demo_builder.meta_info.family_name = 'Demo Color SBIX'
    demo_builder.opentype_config.color_table_formats = {
        opentype.ColorTableFormat.SBIX,
    }

    demo_builder.save_otf(outputs_dir.joinpath('demo.sbix.otf'))
    demo_builder.save_otf_woff(outputs_dir.joinpath('demo.sbix.otf.woff'))
    demo_builder.save_otf_woff2(outputs_dir.joinpath('demo.sbix.otf.woff2'))
    demo_builder.save_ttf(outputs_dir.joinpath('demo.sbix.ttf'))
    demo_builder.save_ttf_woff(outputs_dir.joinpath('demo.sbix.ttf.woff'))
    demo_builder.save_ttf_woff2(outputs_dir.joinpath('demo.sbix.ttf.woff2'))

    demo_builder.meta_info.family_name = 'Demo Color All'
    demo_builder.opentype_config.color_table_formats = {
        opentype.ColorTableFormat.COLR,
        opentype.ColorTableFormat.CBDT,
        opentype.ColorTableFormat.SBIX,
    }

    demo_builder.save_otf(outputs_dir.joinpath('demo.color-all.otf'))
    demo_builder.save_otf_woff(outputs_dir.joinpath('demo.color-all.otf.woff'))
    demo_builder.save_otf_woff2(outputs_dir.joinpath('demo.color-all.otf.woff2'))
    demo_builder.save_ttf(outputs_dir.joinpath('demo.color-all.ttf'))
    demo_builder.save_ttf_woff(outputs_dir.joinpath('demo.color-all.ttf.woff'))
    demo_builder.save_ttf_woff2(outputs_dir.joinpath('demo.color-all.ttf.woff2'))

    demo_collection_builder.save_otc(outputs_dir.joinpath('demo.otc'))
    demo_collection_builder.save_ttc(outputs_dir.joinpath('demo.ttc'))
