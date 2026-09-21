from pathlib import Path

PROJECT_ROOT_DIR = Path(__file__).parents[1]
GLYPHS_DIR = PROJECT_ROOT_DIR.joinpath('assets', 'glyphs')
BUILD_DIR = PROJECT_ROOT_DIR.joinpath('build')
