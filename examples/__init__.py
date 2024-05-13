import logging
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)

project_root_dir = Path(__file__).parent.joinpath('..').resolve()
glyphs_dir = project_root_dir.joinpath('assets', 'glyphs')
build_dir = project_root_dir.joinpath('build')
