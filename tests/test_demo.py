import shutil
from pathlib import Path

from pixel_font_builder import FontBuilder, FontCollectionBuilder


def test_demo(demo_builder: FontBuilder, demo_collection_builder: FontCollectionBuilder, build_dir: Path) -> None:
    outputs_dir = build_dir.joinpath('demo')
    if outputs_dir.exists():
        shutil.rmtree(outputs_dir)
    outputs_dir.mkdir(parents=True)

    demo_builder.save_otf(outputs_dir.joinpath('demo.otf'))
    demo_builder.save_otf_woff(outputs_dir.joinpath('demo.otf.woff'))
    demo_builder.save_otf_woff2(outputs_dir.joinpath('demo.otf.woff2'))
    demo_builder.save_ttf(outputs_dir.joinpath('demo.ttf'))
    demo_builder.save_ttf_woff(outputs_dir.joinpath('demo.ttf.woff'))
    demo_builder.save_ttf_woff2(outputs_dir.joinpath('demo.ttf.woff2'))
    demo_builder.save_ms_bitmap_ttf(outputs_dir.joinpath('demo.ms.bitmap.ttf'))
    demo_builder.save_otb(outputs_dir.joinpath('demo.otb'))
    demo_builder.save_dfont(outputs_dir.joinpath('demo.dfont'))
    demo_builder.save_bdf(outputs_dir.joinpath('demo.bdf'))
    demo_builder.save_pcf(outputs_dir.joinpath('demo.pcf'))

    demo_collection_builder.save_otc(outputs_dir.joinpath('demo.otc'))
    demo_collection_builder.save_ttc(outputs_dir.joinpath('demo.ttc'))
